"""Knowledge packs: what your AI knows about how *you* work.

Built from the owner's own work in the connected dev tools: pull requests they
wrote (and the files they touched), review comments they left, tickets they
closed, and docs they wrote. A pack has three parts, each item with evidence
links back to its sources:

* **skills**: languages, tools and domains, weighted by how much work shows them;
* **style rules**: the standards the owner holds code to ("Money is Decimal, never
  float"). Rules in a known category carry a ``check`` the code reviewer can run;
* **playbooks**: how the owner does recurring work ("Fixing a bug").

The owner reviews and edits the draft (like "Here's what I learned about you" in
onboarding). Rebuilding keeps their edits and never brings back what they
removed. Freezing creates a numbered version, which is what a marketplace
listing points to. Secrets and other people's contact details are scrubbed
before anything enters a pack.
"""
from __future__ import annotations

import json
import os
import re
from collections import Counter, defaultdict
from typing import Any

from coworker.store import Store, iso

SOURCE_KINDS = {"pull_request": "github", "review_comment": "github", "issue": "github", "ticket": "jira",
                "page": "notion"}
MAX_EVIDENCE = 3

# -- scrubbing ------------------------------------------------------------------

SECRET_PATTERNS = [
    re.compile(r"\b(?:ghp|gho|ghs|ghu)_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bsk-(?:ant-)?[A-Za-z0-9_-]{16,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}\b"),
    re.compile(r"\bpat-[a-z0-9]{2,}-[A-Za-z0-9-]{10,}\b"),
    re.compile(r"\b(?:ntn|secret)_[A-Za-z0-9]{20,}\b"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"(?i)\b(password|passwd|api[_-]?key|secret|token)\s*[:=]\s*['\"]?[^\s'\"]{6,}"),
]
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE = re.compile(r"(?<!\d)\+?\d[\d\s().-]{8,}\d(?!\d)")


def scrub(text: str, owner_email: str = "") -> str:
    """Remove secrets and other people's contact details."""
    for pattern in SECRET_PATTERNS:
        text = pattern.sub(lambda m: f"{m.group(1)}=[redacted]" if m.lastindex else "[redacted]", text)
    text = EMAIL.sub(lambda m: m.group(0) if m.group(0).lower() == owner_email.lower() else "[email]", text)
    return PHONE.sub("[phone]", text)


# -- rule categories (shared with the code reviewer) ----------------------------

RULE_CATEGORIES: list[dict[str, Any]] = [
    {"check": "tests", "text": "Every change ships with a test, including the error path.",
     "patterns": [r"\badd (a )?tests?\b", r"\bmissing (a )?tests?\b", r"\btest for\b", r"\bships? with a test\b",
                  r"\bregression test\b", r"\bfailing test first\b"]},
    {"check": "money_decimal", "text": "Money is Decimal, never float.",
     "patterns": [r"\bdecimal\b.*\bfloat\b", r"\bfloat\b.*\bmoney\b", r"\bmoney\b.*\bdecimal\b", r"\bnever float\b"]},
    {"check": "specific_except", "text": "Catch specific exceptions; never a bare except or Exception.",
     "patterns": [r"\bbare (except|exception)\b", r"\bcatch(ing)? (bare )?exception\b", r"\bspecific exceptions?\b"]},
    {"check": "naming", "text": "Names say what they hold (seat_count, not n).",
     "patterns": [r"\bname (this|it)\b", r"\breads? without context\b", r"\bnames? say\b", r"\bbetter name\b"]},
    {"check": "small_pr", "text": "One change per PR; refactors go in their own PR.",
     "patterns": [r"\bone change\b", r"\bsplit\b.*\b(pr|refactor)\b", r"\bown pr\b"]},
    {"check": "early_return", "text": "Prefer early returns over nested ifs.",
     "patterns": [r"\bearly returns?\b", r"\bnested ifs?\b"]},
    {"check": "no_skipped_tests", "text": "Never skip a test to get green: fix it or delete it.",
     "patterns": [r"\bskip(ped)?\b.*\btest", r"\btest\b.*\bskip(ped)?\b", r"\bdon'?t skip\b"]},
    {"check": "docs", "text": "Update the README or docs when behavior changes.",
     "patterns": [r"\bupdate the (readme|docs)\b", r"\bdocument(ed)? in the readme\b"]},
]


def categorize(text: str) -> dict[str, Any] | None:
    lowered = text.lower()
    for cat in RULE_CATEGORIES:
        if any(re.search(p, lowered) for p in cat["patterns"]):
            return cat
    return None


# -- skills -------------------------------------------------------------------------

EXTENSIONS = {".py": "Python", ".ts": "TypeScript", ".tsx": "React", ".jsx": "React", ".js": "JavaScript",
              ".go": "Go", ".rs": "Rust", ".java": "Java", ".kt": "Kotlin", ".rb": "Ruby", ".sql": "SQL",
              ".tf": "Terraform", ".swift": "Swift", ".cs": "C#", ".php": "PHP", ".scala": "Scala"}
PATH_SKILLS = [(r"(^|/)\.github/workflows/", "CI/CD"), (r"(^|/)Dockerfile$|docker-compose", "Docker"),
               (r"(^|/)tests?/|_test\.|\.test\.|test_", "Testing"), (r"(^|/)(k8s|helm|charts)/", "Kubernetes"),
               (r"(^|/)migrations?/", "Database migrations")]
DOMAINS = [(r"\b(billing|pricing|invoice|invoices|discount|payment|stripe|checkout)\b", "Billing & payments"),
           (r"\b(auth|login|oauth|sso|saml|jwt|permission)s?\b", "Auth & identity"),
           (r"\b(api|endpoint|rest|graphql|webhook)s?\b", "APIs"),
           (r"\b(search|index|ranking|embedding)s?\b", "Search"),
           (r"\b(ml|model|training|inference|llm|eval)s?\b", "Machine learning"),
           (r"\b(ui|frontend|component|css|layout)s?\b", "Frontend"),
           (r"\b(deploy|infra|terraform|ecs|kubernetes|ci)\b", "Infrastructure"),
           (r"\b(health|monitoring|alert|logging|observability)\b", "Reliability")]
PREFIXES = {"fix": "Fixing a bug", "feat": "Shipping a feature", "refactor": "Refactoring safely",
            "chore": "Maintenance and dependencies", "perf": "Making it faster", "docs": "Writing docs"}


def _evidence(item: dict[str, Any]) -> dict[str, str]:
    return {"title": (item.get("subject") or "")[:200], "url": (item.get("meta") or {}).get("url", ""),
            "source": SOURCE_KINDS.get(item.get("kind", ""), item.get("provider", ""))}


def _sources(store: Store, user_id: int) -> list[dict[str, Any]]:
    kinds = tuple(SOURCE_KINDS)
    marks = ",".join(["%s"] * len(kinds))
    return store.query(f"SELECT * FROM cw_items WHERE user_id = %s AND kind IN ({marks}) "
                       "ORDER BY occurred_at DESC LIMIT 1000", (user_id, *kinds))


def _skills(prs: list[dict[str, Any]], texts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts: Counter[str] = Counter()
    evidence: dict[str, list[dict[str, str]]] = defaultdict(list)
    for pr in prs:
        found: set[str] = set()
        for f in (pr.get("meta") or {}).get("files") or []:
            path = f.get("path", "")
            ext = os.path.splitext(path)[1]
            if ext in EXTENSIONS:
                found.add(EXTENSIONS[ext])
            found |= {name for pattern, name in PATH_SKILLS if re.search(pattern, path)}
        for name in found:
            counts[name] += 1
            if len(evidence[name]) < MAX_EVIDENCE:
                evidence[name].append(_evidence(pr))
    for item in prs + texts:
        blob = f"{item.get('subject', '')} {item.get('body', '')}".lower()
        for pattern, name in DOMAINS:
            if re.search(pattern, blob):
                counts[name] += 1
                if len(evidence[name]) < MAX_EVIDENCE:
                    evidence[name].append(_evidence(item))
    return [{"id": f"skill-{_slug(name)}", "name": name, "weight": n, "evidence": evidence[name]}
            for name, n in counts.most_common(12)]


def _rules(reviews: list[dict[str, Any]], pages: list[dict[str, Any]], owner_email: str) -> list[dict[str, Any]]:
    by_check: dict[str, dict[str, Any]] = {}
    loose: list[dict[str, Any]] = []
    candidates = [(r.get("body") or "", r) for r in reviews]
    for page in pages:
        if re.search(r"convention|guideline|style|standard", page.get("subject", ""), re.I):
            candidates += [(line.lstrip("-*0123456789. ").strip(), page)
                           for line in (page.get("body") or "").splitlines() if re.match(r"\s*([-*]|\d+\.)\s", line)]
    for text, item in candidates:
        text = scrub(text.strip(), owner_email)
        if not text:
            continue
        cat = categorize(text)
        if cat:
            rule = by_check.setdefault(cat["check"], {"id": f"rule-{cat['check']}", "text": cat["text"],
                                                      "check": cat["check"], "count": 0, "evidence": [], "quotes": []})
            rule["count"] += 1
            if len(rule["evidence"]) < MAX_EVIDENCE:
                rule["evidence"].append(_evidence(item))
            if len(rule["quotes"]) < 2 and item.get("kind") == "review_comment":
                rule["quotes"].append(text[:240])
        elif item.get("kind") == "page" and 8 <= len(text) <= 160 and len(loose) < 8:
            loose.append({"id": f"rule-{_slug(text)[:40]}", "text": text, "check": "", "count": 1,
                          "evidence": [_evidence(item)], "quotes": []})
    rules = sorted(by_check.values(), key=lambda r: -r["count"]) + loose
    return rules[:20]


def _playbooks(prs: list[dict[str, Any]], pages: list[dict[str, Any]], rules: list[dict[str, Any]],
               tickets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    checks = {r["check"] for r in rules}
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for pr in prs:
        m = re.match(r"\s*(\w+)(\(.+?\))?!?:", pr.get("subject") or "")
        if m and m.group(1).lower() in PREFIXES:
            groups[m.group(1).lower()].append(pr)
    playbooks = []
    for prefix, items in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        files = [f.get("path", "") for pr in items for f in (pr.get("meta") or {}).get("files") or []]
        with_tests = sum(1 for pr in items if any(re.search(r"(^|/)tests?/|test_|_test\.|\.test\.", f.get("path", ""))
                                                   for f in (pr.get("meta") or {}).get("files") or []))
        with_docs = sum(1 for f in files if re.search(r"readme|docs/", f, re.I))
        steps = ["Restate the ask as acceptance criteria" if tickets else "Write down what done looks like"]
        if prefix == "fix":
            steps += ["Reproduce it with a failing test", "Make the smallest change that fixes it"]
        elif prefix == "refactor":
            steps += ["Keep behavior identical; tests must pass before and after", "No feature changes in the same PR"]
        else:
            steps += ["Make the smallest change that meets the criteria"]
        if with_tests >= max(1, len(items) // 2) or "tests" in checks:
            steps.append("Add or update tests, including the error path")
        if with_docs or "docs" in checks:
            steps.append("Update the README or docs if behavior changed")
        if "small_pr" in checks:
            steps.append("Keep the PR to this one change")
        steps.append("Open the PR with a clear title and what changed")
        playbooks.append({"id": f"playbook-{prefix}", "title": PREFIXES[prefix], "steps": steps,
                          "evidence": [_evidence(pr) for pr in items[:MAX_EVIDENCE]], "count": len(items)})
    for page in pages:
        lines = [ln.lstrip("-*0123456789. ").strip() for ln in (page.get("body") or "").splitlines()
                 if re.match(r"\s*([-*]|\d+\.)\s", ln)]
        if re.search(r"^how (i|we)\b|playbook|runbook|postmortem", page.get("subject", ""), re.I) and len(lines) >= 2:
            playbooks.append({"id": f"playbook-{_slug(page.get('subject', ''))[:40]}", "title": page.get("subject", ""),
                              "steps": lines[:10], "evidence": [_evidence(page)], "count": 1})
    return playbooks[:10]


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "item"


def extract(store: Store, user_id: int) -> dict[str, Any]:
    """Build pack content from synced items (no edits applied)."""
    owner_email = (store.get_coworker(user_id) or {}).get("owner_email", "")
    items = _sources(store, user_id)
    prs = [i for i in items if i["kind"] == "pull_request" and i.get("direction") == "outbound"]
    reviews = [i for i in items if i["kind"] == "review_comment"]
    tickets = [i for i in items if i["kind"] == "ticket"]
    pages = [i for i in items if i["kind"] == "page"]
    issues = [i for i in items if i["kind"] == "issue"]
    rules = _rules(reviews, pages, owner_email)
    pack = {
        "skills": _skills(prs, tickets + issues + pages),
        "style_rules": rules,
        "playbooks": _playbooks(prs, pages, rules, tickets),
        "stats": {"pull_requests": len(prs), "review_comments": len(reviews), "tickets": len(tickets),
                  "pages": len(pages), "issues": len(issues)},
        "sources": sorted({SOURCE_KINDS[i["kind"]] for i in items}),
    }
    return _refine_with_model(store, user_id, pack, items)


def _refine_with_model(store: Store, user_id: int, pack: dict[str, Any], items: list[dict[str, Any]]) -> dict[str, Any]:
    """With a model, sharpen rule wording and add playbooks the heuristics miss. Offline, return as is."""
    from coworker import llm

    if not llm.available(user_id) or not items:
        return pack
    owner_email = (store.get_coworker(user_id) or {}).get("owner_email", "")
    sample = [{"kind": i["kind"], "title": scrub(i.get("subject") or "", owner_email),
               "text": scrub((i.get("body") or "")[:600], owner_email)} for i in items[:80]]
    prompt = ("Here is a draft profile of how an engineer works, and samples of their own work.\n"
              f"DRAFT:\n{json.dumps({k: pack[k] for k in ('style_rules', 'playbooks')})[:12000]}\n"
              f"SAMPLES:\n{json.dumps(sample)[:20000]}\n\n"
              "Return JSON {\"extra_rules\": [\"...\"], \"extra_playbooks\": [{\"title\": \"...\", \"steps\": [\"...\"]}]} "
              "with at most 5 rules and 3 playbooks the draft is missing, each clearly supported by the samples. "
              "No names, emails, or secrets.")
    try:
        text = llm.complete_text(prompt, system="You extract an engineer's working standards. Output JSON only.",
                                 user_id=user_id, max_tokens=1500)
        data = json.loads(text[text.find("{"): text.rfind("}") + 1])
    except Exception:  # a bad model answer never breaks the pack
        return pack
    for text in (data.get("extra_rules") or [])[:5]:
        text = scrub(str(text), owner_email)[:200]
        if text:
            pack["style_rules"].append({"id": f"rule-{_slug(text)[:40]}", "text": text, "check": "", "count": 1,
                                        "evidence": [], "quotes": [], "model": True})
    for pb in (data.get("extra_playbooks") or [])[:3]:
        steps = [scrub(str(s), owner_email)[:200] for s in (pb.get("steps") or [])][:10]
        if pb.get("title") and steps:
            pack["playbooks"].append({"id": f"playbook-{_slug(str(pb['title']))[:40]}", "title": str(pb["title"])[:120],
                                      "steps": steps, "evidence": [], "count": 1, "model": True})
    return pack


# -- storage, edits, versions ----------------------------------------------------

SECTIONS = ("skills", "style_rules", "playbooks")


def draft(store: Store, user_id: int) -> dict[str, Any] | None:
    return store.one("SELECT * FROM cw_knowledge_packs WHERE user_id = %s AND version = 0", (user_id,))


def build(store: Store, user_id: int) -> dict[str, Any]:
    """Rebuild the draft from current sources, keeping the owner's edits and removals."""
    from coworker.connectors import devtools

    if (store.get_coworker(user_id) or {}).get("mode", "demo") == "demo":
        devtools.ensure_demo(store, user_id)
    fresh = extract(store, user_id)
    existing = draft(store, user_id)
    edits = ((existing or {}).get("pack") or {}).get("edits") or {"removed": [], "changed": {}, "added": {}}
    pack = {**_apply_edits(fresh, edits), "base": fresh}
    sources = fresh.get("sources") or []
    if existing:
        store.update("cw_knowledge_packs", existing["id"], user_id, {"pack": pack, "sources": sources, "updated_at": iso()})
    else:
        store.insert("cw_knowledge_packs", {"user_id": user_id, "version": 0, "status": "draft", "pack": pack,
                                            "sources": sources, "created_at": iso(), "updated_at": iso()})
    store.log(user_id, "knowledge_pack", "Rebuilt your knowledge pack", {k: len(pack[k]) for k in SECTIONS})
    out = draft(store, user_id)
    assert out is not None
    return out


def _apply_edits(pack: dict[str, Any], edits: dict[str, Any]) -> dict[str, Any]:
    removed = set(edits.get("removed") or [])
    changed = edits.get("changed") or {}
    out: dict[str, Any] = {"stats": pack.get("stats") or {}, "edits": edits}
    for section in SECTIONS:
        items = [dict(it, **changed.get(it["id"], {}), edited=it["id"] in changed)
                 for it in pack.get(section) or [] if it["id"] not in removed]
        ids = {it["id"] for it in items}
        items += [dict(it, edited=True) for it in (edits.get("added") or {}).get(section, []) if it["id"] not in ids
                  and it["id"] not in removed]
        out[section] = items
    return out


EDITABLE = {"skills": ("name",), "style_rules": ("text",), "playbooks": ("title", "steps")}


def edit(store: Store, user_id: int, section: str, op: str, item_id: str = "",
         values: dict[str, Any] | None = None) -> dict[str, Any]:
    """``op`` is ``update``, ``remove`` or ``add``. Edits survive every rebuild."""
    if section not in SECTIONS or op not in ("update", "remove", "add"):
        raise ValueError("Unknown section or operation")
    row = draft(store, user_id) or build(store, user_id)
    pack = row["pack"]
    edits = pack.get("edits") or {"removed": [], "changed": {}, "added": {}}
    owner_email = (store.get_coworker(user_id) or {}).get("owner_email", "")
    clean = {k: (scrub(v, owner_email)[:500] if isinstance(v, str) else [scrub(str(s), owner_email)[:300] for s in v][:15])
             for k, v in (values or {}).items() if k in EDITABLE[section] and isinstance(v, str | list)}
    if op == "remove":
        edits["removed"] = sorted(set(edits.get("removed") or []) | {item_id})
    elif op == "update":
        if not any(it["id"] == item_id for it in pack.get(section) or []):
            raise ValueError("No such item")
        edits.setdefault("changed", {})[item_id] = {**edits.get("changed", {}).get(item_id, {}), **clean}
    else:
        if not clean:
            raise ValueError("Nothing to add")
        label = clean.get("text") or clean.get("name") or clean.get("title") or "item"
        new_id = f"{section[:-1] if section.endswith('s') else section}-mine-{_slug(str(label))[:30]}"
        item = {"id": new_id, "evidence": [], "count": 1, "check": "", **clean}
        if section == "style_rules":
            item["check"] = (categorize(str(clean.get("text", ""))) or {}).get("check", "")
        edits.setdefault("added", {}).setdefault(section, []).append(item)
    new_pack = {**_apply_edits(pack.get("base") or {}, edits), "base": pack.get("base") or {}}
    store.update("cw_knowledge_packs", row["id"], user_id, {"pack": new_pack, "updated_at": iso()})
    out = draft(store, user_id)
    assert out is not None
    return out


def freeze(store: Store, user_id: int) -> dict[str, Any]:
    """Save the draft as the next numbered version (what a marketplace listing points to)."""
    row = draft(store, user_id) or build(store, user_id)
    latest = store.one("SELECT MAX(version) AS v FROM cw_knowledge_packs WHERE user_id = %s", (user_id,))
    version = int((latest or {}).get("v") or 0) + 1
    pack = {k: v for k, v in row["pack"].items() if k not in ("edits", "base")}
    store.insert("cw_knowledge_packs", {"user_id": user_id, "version": version, "status": "frozen", "pack": pack,
                                        "sources": row.get("sources") or [], "created_at": iso(), "updated_at": iso()})
    store.log(user_id, "knowledge_pack", f"Saved knowledge pack version {version}")
    out = store.one("SELECT * FROM cw_knowledge_packs WHERE user_id = %s AND version = %s", (user_id, version))
    assert out is not None
    return out


def versions(store: Store, user_id: int) -> list[dict[str, Any]]:
    return store.query("SELECT id, version, status, sources, created_at FROM cw_knowledge_packs "
                       "WHERE user_id = %s AND version > 0 ORDER BY version DESC", (user_id,))


def forget_source(store: Store, user_id: int) -> None:
    """After a source is disconnected (and its items deleted), drop what came from it."""
    if draft(store, user_id):
        build(store, user_id)


def current(store: Store, user_id: int) -> dict[str, Any]:
    """The pack the coworker works from: a hired AI's pack while a hire is active, else your own draft."""
    from coworker import marketplace

    hired = marketplace.hired_pack(store, user_id)
    if hired:
        return hired
    row = draft(store, user_id)
    return (row or build(store, user_id))["pack"]


def prompt_context(pack: dict[str, Any], limit: int = 12) -> str:
    """The pack as prompt text, with ids the model cites as [rule-…] / [playbook-…]."""
    lines = ["How the owner works (cite ids you rely on):"]
    lines += [f"- [{r['id']}] {r['text']}" for r in (pack.get("style_rules") or [])[:limit]]
    for pb in (pack.get("playbooks") or [])[:4]:
        lines.append(f"- [{pb['id']}] {pb['title']}: " + "; ".join(pb.get("steps") or []))
    skills = ", ".join(s["name"] for s in (pack.get("skills") or [])[:8])
    if skills:
        lines.append(f"Skills: {skills}")
    return "\n".join(lines)


def serialize(row: dict[str, Any]) -> dict[str, Any]:
    pack = row.get("pack") or {}
    return {"id": row["id"], "version": row["version"], "status": row["status"],
            "skills": pack.get("skills") or [], "styleRules": pack.get("style_rules") or [],
            "playbooks": pack.get("playbooks") or [], "stats": pack.get("stats") or {},
            "sources": row.get("sources") or [], "updatedAt": row.get("updated_at")}
