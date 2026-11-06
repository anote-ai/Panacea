"""Spec: turn a chat message, Jira ticket, Notion page or GitHub issue into a structured spec.

A spec is ``{goal, acceptance_criteria, constraints, repo, source}``. The human
confirms (and can edit) it before anything is planned.
"""
from __future__ import annotations

import json
import re
from typing import Any

from coworker.store import Store

BULLET = re.compile(r"^\s*(?:[-*•]|\d+[.)]|- \[ \])\s+(.+)$")
CRITERIA_HEADING = re.compile(r"acceptance criteria|definition of done|requirements|done when", re.I)
NEGATIVE = re.compile(r"^(don'?t|do not|never|must not|avoid|without)\b", re.I)
CONSTRAINT = re.compile(r"\b(don'?t|do not|must not|never|without|keep|only|avoid|backwards?.compatible)\b", re.I)
REQUIREMENT = re.compile(r"\b(should|must|returns?|when|raises?|shows?|supports?|adds?)\b", re.I)
SOURCE = re.compile(r"^(jira|notion|github):(.+)$")


def parse_source(ref: str) -> tuple[str, str]:
    m = SOURCE.match(ref.strip())
    if not m:
        raise ValueError("Source must look like jira:KEY-1, notion:<page id>, or github:owner/repo#12")
    return m.group(1), m.group(2).strip()


def fetch_source(store: Store, user_id: int, ref: str) -> dict[str, Any]:
    """Title, text and link for a ticket, page or issue."""
    from coworker.connectors import devtools

    kind, value = parse_source(ref)
    client = devtools.require(store, user_id, kind)
    if kind == "jira":
        issue = client.issue(value.upper())
        return {"kind": "jira", "ref": issue["key"], "title": issue["summary"], "text": issue["description"],
                "url": issue["url"]}
    if kind == "notion":
        page = client.page(value)
        return {"kind": "notion", "ref": value, "title": page["title"], "text": page["text"], "url": page["url"]}
    repo, _, number = value.partition("#")
    if not number.isdigit():
        raise ValueError("Use github:owner/repo#number")
    body = client.request("GET", f"/repos/{repo}/issues/{number}") if hasattr(client, "request") else {}
    return {"kind": "github", "ref": value, "title": body.get("title", ""), "text": body.get("body") or "",
            "url": body.get("html_url", ""), "repo": repo}


def heuristic(title: str, text: str) -> dict[str, Any]:
    lines = [ln.rstrip() for ln in (text or "").splitlines()]
    criteria: list[str] = []
    constraints: list[str] = []
    in_criteria = False
    prose: list[str] = []
    for line in lines:
        if not line.strip():
            continue
        if CRITERIA_HEADING.search(line) and not BULLET.match(line):
            in_criteria = True
            continue
        m = BULLET.match(line)
        if m:
            item = m.group(1).strip()
            is_constraint = NEGATIVE.match(item) or (CONSTRAINT.search(item) and not in_criteria)
            (constraints if is_constraint else criteria).append(item)
        else:
            prose.append(line.strip())
            in_criteria = False
    if not criteria:
        for sentence in re.split(r"(?<=[.!?])\s+", " ".join(prose)):
            if len(sentence) <= 10:
                continue
            if NEGATIVE.match(sentence) or re.match(r"(keep|only)\b", sentence, re.I):
                constraints.append(sentence.strip())
            elif REQUIREMENT.search(sentence):
                criteria.append(sentence.strip())
    goal = (title or (prose[0] if prose else "") or (criteria[0] if criteria else "")).strip()
    return {"goal": goal[:300], "acceptance_criteria": criteria[:15], "constraints": constraints[:10]}


def _refine(spec: dict[str, Any], text: str, user_id: int) -> dict[str, Any]:
    from coworker import llm

    if not llm.available(user_id):
        return spec
    prompt = (f"Turn this request into a spec.\nREQUEST:\n{text[:8000]}\n\nDRAFT:\n{json.dumps(spec)}\n\n"
              "Return JSON {\"goal\": str, \"acceptance_criteria\": [str], \"constraints\": [str]}. Criteria must be "
              "testable. Don't invent requirements that aren't asked for.")
    try:
        out = llm.complete_text(prompt, system="You write precise engineering specs. Output JSON only.", user_id=user_id,
                                max_tokens=1500)
        data = json.loads(out[out.find("{"): out.rfind("}") + 1])
    except Exception:
        return spec
    return {"goal": str(data.get("goal") or spec["goal"])[:300],
            "acceptance_criteria": [str(c)[:300] for c in data.get("acceptance_criteria") or spec["acceptance_criteria"]][:15],
            "constraints": [str(c)[:300] for c in data.get("constraints") or spec["constraints"]][:10]}


def make(store: Store, user_id: int, *, text: str = "", source: str = "", repo: str = "") -> dict[str, Any]:
    src: dict[str, Any] = {"kind": "chat", "ref": "", "title": "", "url": ""}
    if source:
        src = fetch_source(store, user_id, source)
        text = f"{src['title']}\n\n{src['text']}"
    if not text.strip():
        raise ValueError("Describe what to build, or give a ticket")
    spec = heuristic(src.get("title", ""), text if not src.get("title") else src["text"])
    if not spec["goal"]:
        spec["goal"] = text.strip().splitlines()[0][:300]
    spec = _refine(spec, text, user_id)
    spec["repo"] = repo or src.get("repo") or default_repo(store, user_id)
    spec["source"] = {k: src.get(k, "") for k in ("kind", "ref", "title", "url")}
    return spec


def default_repo(store: Store, user_id: int) -> str:
    from coworker.connectors.devtools_demo import REPO

    coworker = store.get_coworker(user_id) or {}
    repo = str((coworker.get("settings") or {}).get("default_repo") or "")
    if repo:
        return repo
    return REPO if coworker.get("mode", "demo") == "demo" else ""


def validate(spec: dict[str, Any]) -> dict[str, Any]:
    goal = str(spec.get("goal", "")).strip()
    criteria = [str(c).strip()[:300] for c in spec.get("acceptance_criteria") or [] if str(c).strip()]
    if not goal:
        raise ValueError("The spec needs a goal")
    if not criteria:
        raise ValueError("Add at least one acceptance criterion")
    repo = str(spec.get("repo", "")).strip()
    if repo.count("/") != 1:
        raise ValueError("Pick the repository (owner/name)")
    return {"goal": goal[:300], "acceptance_criteria": criteria[:15],
            "constraints": [str(c).strip()[:300] for c in spec.get("constraints") or [] if str(c).strip()][:10],
            "repo": repo, "source": spec.get("source") or {"kind": "chat"}}
