"""Graph engineering: break a spec into a dependency graph of tasks.

Each node is ``{id, title, kind, files, depends_on, criteria}``. Nodes in the same
layer don't depend on each other, so they can run in parallel. The graph is
shown (and editable) before anything runs.
"""
from __future__ import annotations

import json
import os
import re
from typing import Any

from coworker.engineering.diffs import is_code, is_test

KINDS = ("interface", "impl", "test", "docs", "migration", "config")
INTERFACE_WORDS = re.compile(r"\b(api|endpoint|interface|schema|contract|route)\b", re.I)
DOC_WORDS = re.compile(r"\b(readme|docs?|documented|documentation)\b", re.I)
WORD = re.compile(r"[a-z][a-z0-9]+")
STOP = {"the", "and", "for", "with", "when", "that", "this", "from", "into", "should", "must", "returns", "return",
        "add", "adds", "still", "same", "than", "fewer", "more", "each", "raises", "apply", "applies", "paying", "get"}


class GraphError(ValueError):
    pass


def _words(text: str) -> set[str]:
    text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text).replace("_", " ").replace("/", " ").replace(".", " ").lower()
    return {w for w in WORD.findall(text) if w not in STOP and len(w) > 2}


def _stem(word: str) -> str:
    return re.sub(r"(ing|ed|es|s)$", "", word)


def rank_files(spec: dict[str, Any], files: list[str], contents: dict[str, str] | None = None) -> list[str]:
    want = {_stem(w) for w in _words(" ".join([spec["goal"], *spec["acceptance_criteria"]]))}
    scored = []
    for path in files:
        if not is_code(path) or is_test(path) or os.path.basename(path) == "__init__.py":
            continue
        have = {_stem(w) for w in _words(path)}
        if contents and path in contents:
            have |= {_stem(w) for w in _words(contents[path][:4000])}
        score = len(want & have)
        if score:
            scored.append((score, path))
    return [p for _, p in sorted(scored, key=lambda sp: (-sp[0], sp[1]))]


def _test_path_for(path: str, files: list[str], goal: str) -> str:
    base = os.path.splitext(os.path.basename(path))[0]
    ext = os.path.splitext(path)[1]
    for candidate in files:
        if is_test(candidate) and base in candidate:
            return candidate
    slug = re.sub(r"[^a-z0-9]+", "_", goal.lower()).strip("_")[:30] or base
    if ext == ".py":
        return f"tests/test_{slug}.py"
    return f"{os.path.splitext(path)[0]}.test{ext}"


def heuristic(spec: dict[str, Any], files: list[str], contents: dict[str, str] | None = None) -> list[dict[str, Any]]:
    targets = rank_files(spec, files, contents)[:3]
    if not targets:
        slug = re.sub(r"[^a-z0-9]+", "_", spec["goal"].lower()).strip("_")[:30] or "feature"
        targets = [f"{slug}.py"]
    criteria = list(range(len(spec["acceptance_criteria"])))
    text = " ".join([spec["goal"], *spec["acceptance_criteria"]])
    nodes: list[dict[str, Any]] = []
    impl_deps: list[str] = []
    if INTERFACE_WORDS.search(text):
        nodes.append({"id": "interface", "title": "Define the interface (signatures, types, routes)", "kind": "interface",
                      "files": targets[:1], "depends_on": [], "criteria": criteria})
        impl_deps = ["interface"]
    nodes.append({"id": "impl", "title": f"Implement: {spec['goal']}", "kind": "impl", "files": targets,
                  "depends_on": impl_deps, "criteria": criteria})
    nodes.append({"id": "test", "title": "Test every acceptance criterion, including the error path", "kind": "test",
                  "files": [_test_path_for(targets[0], files, spec["goal"])], "depends_on": ["impl"], "criteria": criteria})
    if DOC_WORDS.search(text) or "README.md" in files:
        doc_criteria = [i for i, c in enumerate(spec["acceptance_criteria"]) if DOC_WORDS.search(c)]
        if doc_criteria or DOC_WORDS.search(text):
            nodes.append({"id": "docs", "title": "Document the new behavior", "kind": "docs",
                          "files": ["README.md"], "depends_on": ["impl"], "criteria": doc_criteria})
    return nodes


def validate(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not nodes:
        raise GraphError("The graph needs at least one task")
    if len(nodes) > 20:
        raise GraphError("Keep it to 20 tasks or fewer")
    clean = []
    ids: set[str] = set()
    for n in nodes:
        node_id = re.sub(r"[^a-z0-9_-]+", "-", str(n.get("id", "")).lower()).strip("-")[:40]
        if not node_id or node_id in ids:
            raise GraphError(f"Task ids must be unique and non-empty ('{n.get('id')}')")
        ids.add(node_id)
        kind = n.get("kind") if n.get("kind") in KINDS else "impl"
        files = [str(f).strip().lstrip("/") for f in n.get("files") or [] if str(f).strip()][:10]
        if any(".." in f.split("/") for f in files):
            raise GraphError("File paths must stay inside the repository")
        clean.append({"id": node_id, "title": str(n.get("title") or node_id)[:200], "kind": kind, "files": files,
                      "depends_on": [str(d) for d in n.get("depends_on") or []],
                      "criteria": [int(c) for c in n.get("criteria") or [] if str(c).isdigit()]})
    for n in clean:
        missing = [d for d in n["depends_on"] if d not in ids]
        if missing:
            raise GraphError(f"'{n['id']}' depends on unknown task(s): {', '.join(missing)}")
    layers(clean)
    return clean


def layers(nodes: list[dict[str, Any]]) -> list[list[str]]:
    """Topological layers; nodes within a layer are independent."""
    remaining = {n["id"]: set(n["depends_on"]) for n in nodes}
    done: set[str] = set()
    out: list[list[str]] = []
    while remaining:
        ready = sorted(i for i, deps in remaining.items() if deps <= done)
        if not ready:
            raise GraphError(f"The graph has a cycle among: {', '.join(sorted(remaining))}")
        out.append(ready)
        done |= set(ready)
        for i in ready:
            remaining.pop(i)
    return out


def plan(spec: dict[str, Any], files: list[str], contents: dict[str, str] | None = None,
         user_id: int | None = None) -> list[dict[str, Any]]:
    from coworker import llm

    fallback = heuristic(spec, files, contents)
    if not llm.available(user_id):
        return fallback
    prompt = (f"SPEC:\n{json.dumps(spec)[:6000]}\n\nREPOSITORY FILES:\n" + "\n".join(files[:400]) +
              "\n\nBreak the spec into a small dependency graph of tasks. Return JSON {\"nodes\": [{\"id\": str, "
              "\"title\": str, \"kind\": one of " + ", ".join(KINDS) + ", \"files\": [paths], \"depends_on\": [ids], "
              "\"criteria\": [indexes of acceptance criteria]}]}. Prefer few tasks; tests and docs depend on the code they cover.")
    try:
        out = llm.complete_text(prompt, system="You plan software changes as task graphs. Output JSON only.",
                                user_id=user_id, max_tokens=2000)
        return validate(json.loads(out[out.find("{"): out.rfind("}") + 1]).get("nodes") or [])
    except Exception:
        return fallback
