"""The AI code reviewer.

Reviews a change (a GitHub pull request, or the AI engineer's own output) the way
the owner would: universal checks every reviewer should make, plus the checks
behind the style rules in the owner's knowledge pack. With a model, it also
looks for correctness bugs. Each finding has a severity, a location, and a
suggested fix, and cites the pack rule it applies.

Dismissing a finding with "don't flag this in this repo" stores a suppression,
so later reviews learn from feedback the way rejected drafts do today.

It escalates to the human in the loop when a finding is high severity, when it
touches auth, payments or security code, or when the model isn't sure.
"""
from __future__ import annotations

import fnmatch
import json
import re
from typing import Any

from coworker.engineering import slop
from coworker.engineering.diffs import from_github_files, is_code, is_test, size
from coworker.knowledge_pack import SECRET_PATTERNS
from coworker.store import Store, iso

SENSITIVE = re.compile(r"(^|/)(auth|oauth|login|sso|payments?|billing|stripe|checkout|security|crypto|secrets?|"
                       r"permissions?|iam)(/|\.|_)", re.I)
MONEY = re.compile(r"price|amount|total|money|refund|invoice|cost|charge|balance|subtotal|fee", re.I)
FLOAT_USE = re.compile(r"\bfloat\(|\bround\([^)]*\*|:\s*float\b|->\s*float\b")
SHORT_PARAM = re.compile(r"^\s*def\s+\w+\(([^)]*)\)")
SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2}

# Checks every review runs, whatever the pack says.
UNIVERSAL = {"secret", "no_skipped_tests", "specific_except", "tests", "weakened_test", "debug_left"}
# Checks that only run when the owner's pack has the matching style rule.
PACK_CHECKS = {"money_decimal", "naming", "early_return", "small_pr", "docs"}


def _finding(check: str, severity: str, path: str, line: int, title: str, detail: str, suggestion: str, *,
             rules: dict[str, str]) -> dict[str, Any]:
    return {"id": f"{check}:{path}:{line}", "check": check, "severity": severity, "path": path, "line": line,
            "title": title, "detail": detail[:500], "suggestion": suggestion[:500], "rule": rules.get(check, ""),
            "dismissed": False}


def static_findings(changes: list[dict[str, Any]], pack: dict[str, Any] | None) -> list[dict[str, Any]]:
    rules = {r.get("check"): r["id"] for r in (pack or {}).get("style_rules") or [] if r.get("check")}
    enabled = UNIVERSAL | (PACK_CHECKS & set(rules))
    out: list[dict[str, Any]] = []

    def add(check: str, *args: Any) -> None:
        if check in enabled:
            out.append(_finding(check, *args, rules=rules))

    code_changed = [c for c in changes if is_code(c["path"]) and not is_test(c["path"]) and c["added"]]
    tests_changed = [c for c in changes if is_test(c["path"])]
    for c in changes:
        path = c["path"]
        for line, text in c["added"]:
            if any(p.search(text) for p in SECRET_PATTERNS[:8]):
                add("secret", "high", path, line, "A secret is committed", "This line looks like a credential.",
                    "Remove it, rotate the credential, and load it from the environment.")
            if slop.SKIP.search(text):
                add("no_skipped_tests", "high", path, line, "A test is skipped",
                    "Skipping a test hides the failure instead of fixing it.", "Fix the test, or delete it if it's wrong.")
            if path.endswith(".py") and slop.BARE_EXCEPT.match(text):
                add("specific_except", "medium", path, line, "Catches every exception",
                    "Real bugs (typos, None) get swallowed here.", "Catch the specific exception you expect.")
            if not is_test(path) and slop.DEBUG.search(text):
                add("debug_left", "low", path, line, "Debug output left in", text.strip(), "Remove it or use the logger.")
            if path.endswith(".py") and FLOAT_USE.search(text) and (MONEY.search(text) or MONEY.search(path)):
                add("money_decimal", "high", path, line, "Money as float",
                    "Floats lose cents (0.1 + 0.2 != 0.3).", "Keep it Decimal and quantize to cents.")
            if path.endswith(".py") and (m := SHORT_PARAM.match(text)):
                short = [p.split(":")[0].split("=")[0].strip() for p in m.group(1).split(",")]
                bad = [p for p in short if len(p) == 1 and p not in ("_",)]
                if bad:
                    add("naming", "low", path, line, "Unclear names", f"Parameter(s) {', '.join(bad)}",
                        "Name parameters for what they hold.")
        _nested_ifs(c, add)
    if code_changed and not tests_changed:
        first = code_changed[0]
        add("tests", "medium", first["path"], first["added"][0][0], "No test for this change",
            f"{len(code_changed)} code file(s) changed and no test did.", "Add a test, including the error path.")
    for c in tests_changed:
        removed = sum(1 for t in c["removed"] if slop.ASSERT.search(t))
        if removed > sum(1 for _, t in c["added"] if slop.ASSERT.search(t)):
            add("weakened_test", "high", c["path"], 0, "Assertions removed from a test",
                f"{removed} assertion(s) removed.", "Keep the assertions; change the code, not the test.")
    if size(changes) > 400 or len(changes) > 12:
        add("small_pr", "low", "", 0, "Large pull request", f"{size(changes)} lines across {len(changes)} files.",
            "Split it into one change per PR.")
    if code_changed and not any(re.search(r"readme|docs/", c["path"], re.I) for c in changes) and \
            any(re.match(r"\s*def [a-z]", t) for c in code_changed for _, t in c["added"]):
        add("docs", "low", code_changed[0]["path"], 0, "Docs not updated",
            "New behavior, but no README or docs change.", "Document the new behavior.")
    return out


def _nested_ifs(change: dict[str, Any], add: Any) -> None:
    stack: list[int] = []
    for line, text in change["added"]:
        if not text.strip():
            continue
        indent = len(text) - len(text.lstrip())
        stack = [i for i in stack if i < indent]
        if re.match(r"\s*if\b", text):
            stack.append(indent)
            if len(stack) >= 2:
                add("early_return", "low", change["path"], line, "Nested ifs",
                    "Two levels of if where an early return reads better.", "Return early for the edge case.")
                stack = []


def _model_findings(changes: list[dict[str, Any]], pack: dict[str, Any] | None, user_id: int | None) -> tuple[list[dict[str, Any]], bool]:
    """Correctness review by a model. Returns (findings, unsure)."""
    from coworker import knowledge_pack, llm

    if not llm.available(user_id):
        return [], False
    diff = "\n".join(c.get("patch") or "" for c in changes)[:30000]
    prompt = (f"{knowledge_pack.prompt_context(pack or {})}\n\nReview this diff for correctness bugs, security problems and "
              "missing edge cases. Ignore style the rules above don't mention.\n"
              f"DIFF:\n{diff}\n\nReturn JSON {{\"findings\": [{{\"path\": str, \"line\": int, \"severity\": "
              "\"high\"|\"medium\"|\"low\", \"title\": str, \"detail\": str, \"suggestion\": str, \"rule\": str}}], "
              "\"unsure\": bool}. Only real problems; an empty list is fine.")
    try:
        text = llm.complete_text(prompt, system="You are a senior engineer reviewing a pull request. Output JSON only.",
                                 user_id=user_id, max_tokens=3000, effort="medium")
        data = json.loads(text[text.find("{"): text.rfind("}") + 1])
    except Exception:
        return [], True
    found: list[dict[str, Any]] = []
    for f in (data.get("findings") or [])[:20]:
        sev = f.get("severity") if f.get("severity") in SEVERITY_ORDER else "medium"
        found.append({"id": f"model:{f.get('path', '')}:{f.get('line', 0)}:{len(found)}", "check": "model",
                      "severity": sev, "path": str(f.get("path", "")), "line": int(f.get("line") or 0),
                      "title": str(f.get("title", ""))[:200], "detail": str(f.get("detail", ""))[:500],
                      "suggestion": str(f.get("suggestion", ""))[:500], "rule": str(f.get("rule", ""))[:80],
                      "dismissed": False})
    return found, bool(data.get("unsure"))


def suppressed(finding: dict[str, Any], repo: str, suppressions: list[dict[str, Any]]) -> bool:
    return any(s.get("check") == finding["check"] and s.get("repo") in ("", repo)
               and fnmatch.fnmatch(finding.get("path", ""), s.get("path") or "*") for s in suppressions)


def review_changes(changes: list[dict[str, Any]], *, pack: dict[str, Any] | None, repo: str = "",
                   suppressions: list[dict[str, Any]] | None = None, user_id: int | None = None,
                   use_model: bool = True) -> dict[str, Any]:
    findings = static_findings(changes, pack)
    unsure = False
    if use_model:
        extra, unsure = _model_findings(changes, pack, user_id)
        seen = {(f["path"], f["line"]) for f in findings}
        findings += [f for f in extra if (f["path"], f["line"]) not in seen]
    findings = [f for f in findings if not suppressed(f, repo, suppressions or [])]
    findings.sort(key=lambda f: (SEVERITY_ORDER[f["severity"]], f["path"], f["line"]))
    reasons = []
    if any(f["severity"] == "high" for f in findings):
        reasons.append("high-severity findings")
    sensitive = sorted({c["path"] for c in changes if SENSITIVE.search(c["path"])})
    if sensitive:
        reasons.append(f"touches sensitive code ({', '.join(sensitive[:3])})")
    if unsure:
        reasons.append("the reviewer wasn't sure")
    counts = {s: sum(1 for f in findings if f["severity"] == s) for s in SEVERITY_ORDER}
    summary = ("No problems found." if not findings else
               f"{len(findings)} finding(s): {counts['high']} high, {counts['medium']} medium, {counts['low']} low.")
    return {"findings": findings, "summary": summary, "escalate": bool(reasons), "reasons": reasons,
            "slop": slop.report(changes)}


# -- persistence and GitHub ------------------------------------------------------------

def suppressions_for(store: Store, user_id: int) -> list[dict[str, Any]]:
    return list(((store.get_coworker(user_id) or {}).get("settings") or {}).get("review_suppressions") or [])


def _pack(store: Store, user_id: int) -> dict[str, Any]:
    from coworker import knowledge_pack

    return knowledge_pack.current(store, user_id)


def save(store: Store, user_id: int, result: dict[str, Any], *, repo: str, number: int = 0, source: str = "pr",
         run_id: int | None = None) -> dict[str, Any]:
    review_id = store.insert("cw_reviews", {
        "user_id": user_id, "repo": repo, "number": number, "source": source, "run_id": run_id, "status": "done",
        "findings": result["findings"], "checks": {"text": result["summary"], "reasons": result["reasons"],
                                                    "slop": result["slop"]},
        "escalate": int(result["escalate"]), "created_at": iso()})
    row = store.get("cw_reviews", review_id, user_id)
    assert row is not None
    return row


def review_pull_request(store: Store, user_id: int, repo: str, number: int) -> dict[str, Any]:
    """Review a PR on GitHub and propose posting the review (inline comments) for approval."""
    from coworker import executor
    from coworker.connectors import devtools

    client = devtools.require(store, user_id, "github")
    changes = from_github_files(client.pr_files(repo, number))
    result = review_changes(changes, pack=_pack(store, user_id), repo=repo,
                            suppressions=suppressions_for(store, user_id), user_id=user_id)
    row = save(store, user_id, result, repo=repo, number=number)
    comments = [{"path": f["path"], "line": f["line"],
                 "body": f"**{f['title']}** ({f['severity']})\n\n{f['detail']}\n\nSuggestion: {f['suggestion']}"}
                for f in result["findings"] if f["path"] and f["line"]]
    body = f"AI code review: {result['summary']}"
    if result["escalate"]:
        body += f"\n\nFlagged for a human reviewer: {'; '.join(result['reasons'])}."
    risks = [{"code": "review_escalation", "message": f"Needs a human look: {'; '.join(result['reasons'])}."}] \
        if result["escalate"] else []
    action = executor.propose(store, user_id, "github.review",
                              {"repo": repo, "number": number, "body": body, "comments": comments,
                               "event": "REQUEST_CHANGES" if any(f["severity"] == "high" for f in result["findings"])
                               else "COMMENT", "review_id": row["id"]},
                              title=f"Review {repo}#{number}: {result['summary']}", reasoning=body, extra_risks=risks)
    store.update("cw_reviews", row["id"], user_id, {"action_id": action["id"]})
    store.log(user_id, "review", f"Reviewed {repo}#{number}: {result['summary']}", {"review_id": row["id"]})
    fresh = store.get("cw_reviews", row["id"], user_id)
    assert fresh is not None
    return fresh


def dismiss(store: Store, user_id: int, review_id: int, finding_id: str, scope: str = "once") -> dict[str, Any]:
    """Dismiss a finding. ``scope="repo"`` (or ``"everywhere"``) also stops flagging that check there."""
    row = store.get("cw_reviews", review_id, user_id)
    if not row:
        raise LookupError("No such review")
    findings = row.get("findings") or []
    match = next((f for f in findings if f["id"] == finding_id), None)
    if not match:
        raise LookupError("No such finding")
    match["dismissed"] = True
    store.update("cw_reviews", review_id, user_id, {"findings": findings})
    if scope in ("repo", "everywhere"):
        coworker = store.get_coworker(user_id) or {}
        settings = coworker.get("settings") or {}
        rule = {"check": match["check"], "repo": row["repo"] if scope == "repo" else "", "path": "*"}
        current = [s for s in settings.get("review_suppressions") or [] if s != rule]
        store.update_coworker(user_id, settings={**settings, "review_suppressions": current + [rule]})
        where = f"in {row['repo']}" if scope == "repo" else "anywhere"
        store.log(user_id, "review_feedback", f"Won't flag '{match['title']}' {where} again", rule)
    fresh = store.get("cw_reviews", review_id, user_id)
    assert fresh is not None
    return fresh


def serialize(row: dict[str, Any]) -> dict[str, Any]:
    summary = row.get("checks") or {}
    return {"id": row["id"], "repo": row["repo"], "number": row["number"], "source": row["source"],
            "runId": row.get("run_id"), "findings": row.get("findings") or [], "summary": summary.get("text", ""),
            "reasons": summary.get("reasons") or [], "slop": summary.get("slop") or {},
            "escalate": bool(row.get("escalate")), "actionId": row.get("action_id"), "createdAt": row["created_at"]}
