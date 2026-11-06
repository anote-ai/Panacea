"""Slop detection for AI-written code: the things a careful reviewer sends back.

``report(changes, ...)`` returns a 0-100 score (100 = clean) and the flags that
cost points. It runs on every pull request the AI engineer proposes and on
reviewed PRs, and autonomy rules can require a minimum score.
"""
from __future__ import annotations

import re
import sys
from collections import Counter
from typing import Any

from coworker.engineering.diffs import is_code, is_test, size

SKIP = re.compile(r"@pytest\.mark\.skip|pytest\.skip\(|@unittest\.skip|\b(it|test|describe)\.skip\(|\bx(it|describe)\(|"
                  r"t\.Skip\(|#\[ignore\]")
ASSERT = re.compile(r"\bassert\b|\bexpect\(|\bassertEqual|\bassert_\w+\(|\.should\b")
TODO = re.compile(r"\b(TODO|FIXME|XXX|HACK)\b")
DEBUG = re.compile(r"^\s*print\(|console\.log\(|\bdebugger;|pdb\.set_trace\(|breakpoint\(\)")
BARE_EXCEPT = re.compile(r"^\s*except\s*(Exception\s*)?(as \w+\s*)?:")
COMMENT = re.compile(r"^\s*(#|//)\s*(.+)$")
PY_IMPORT = re.compile(r"^\s*(?:from\s+([\w.]+)\s+import|import\s+([\w.]+))")
PY_DEF = re.compile(r"^\s*def\s+([a-zA-Z_]\w*)\s*\(")
WORD = re.compile(r"[a-z]+")

# Test tooling a test file may import without it being listed anywhere we can see.
TEST_LIBRARIES = {"pytest", "hypothesis", "mock", "freezegun", "responses", "factory", "faker", "pytest_mock"}

WEIGHTS = {"skipped_test": 25, "weakened_test": 20, "huge_diff": 15, "unknown_import": 15, "duplicated_block": 8,
           "dead_code": 6, "todo_left": 5, "debug_left": 5, "bare_except": 5, "restating_comment": 3}
MESSAGES = {
    "skipped_test": "A test was skipped instead of fixed.",
    "weakened_test": "Assertions were removed from a test.",
    "huge_diff": "The change is much bigger than the ask.",
    "unknown_import": "Imports a module that isn't in the repo, its requirements, or the standard library. Invented API?",
    "duplicated_block": "The same line is repeated instead of shared.",
    "dead_code": "Adds a function nothing calls.",
    "todo_left": "Leaves a TODO behind.",
    "debug_left": "Leaves debugging output behind.",
    "bare_except": "Swallows every exception.",
    "restating_comment": "A comment that only restates the code.",
}


def _restates(comment: str, code: str) -> bool:
    words = set(WORD.findall(comment.lower())) - {"the", "a", "an", "to", "of", "and", "this", "we", "it", "is"}
    code_words = set(WORD.findall(re.sub(r"([a-z])([A-Z])", r"\1 \2", code).replace("_", " ").lower()))
    return len(words) >= 2 and len(words & code_words) / len(words) >= 0.7


def report(changes: list[dict[str, Any]], *, criteria: int = 0, known_modules: set[str] | None = None,
           requirements: str = "", existing_code: str = "") -> dict[str, Any]:
    flags: list[dict[str, Any]] = []

    def flag(code: str, path: str = "", line: int = 0, detail: str = "") -> None:
        flags.append({"code": code, "message": MESSAGES[code], "path": path, "line": line, "detail": detail[:200],
                      "weight": WEIGHTS[code]})

    added_text = "\n".join(t for c in changes for _, t in c["added"])
    known = set(known_modules or set()) | set(sys.stdlib_module_names) | {
        c["path"].split("/")[0].removesuffix(".py") for c in changes}  # the repo's own packages
    reqs = {re.split(r"[<>=\[ ;]", r.strip())[0].lower().replace("-", "_") for r in requirements.splitlines() if r.strip()}
    line_counts: Counter[str] = Counter(t.strip() for c in changes for _, t in c["added"]
                                        if len(t.strip()) > 25 and not COMMENT.match(t))
    for c in changes:
        path = c["path"]
        test_file = is_test(path)
        added = c["added"]
        if test_file:
            removed_asserts = sum(1 for t in c["removed"] if ASSERT.search(t))
            added_asserts = sum(1 for _, t in added if ASSERT.search(t))
            if removed_asserts > added_asserts:
                flag("weakened_test", path, 0, f"{removed_asserts} assertions removed, {added_asserts} added")
        for i, (line, text) in enumerate(added):
            if SKIP.search(text):
                flag("skipped_test", path, line, text.strip())
            if TODO.search(text):
                flag("todo_left", path, line, text.strip())
            if not test_file and DEBUG.search(text):
                flag("debug_left", path, line, text.strip())
            if path.endswith(".py") and BARE_EXCEPT.match(text):
                flag("bare_except", path, line, text.strip())
            m = COMMENT.match(text)
            if m and i + 1 < len(added) and _restates(m.group(2), added[i + 1][1]):
                flag("restating_comment", path, line, m.group(2))
            if path.endswith(".py") and (im := PY_IMPORT.match(text)):
                module = (im.group(1) or im.group(2) or "").split(".")[0]
                if test_file and module in TEST_LIBRARIES:
                    continue
                if module and not module.startswith("_") and module not in known and module.lower() not in reqs:
                    flag("unknown_import", path, line, module)
            if path.endswith(".py") and not test_file and (d := PY_DEF.match(text)):
                name = d.group(1)
                used = len(re.findall(rf"\b{re.escape(name)}\b", added_text + "\n" + existing_code))
                if used <= 1 and not name.startswith("_") and name not in ("main",):
                    flag("dead_code", path, line, name)
    for text, n in line_counts.items():
        if n >= 3:
            flag("duplicated_block", "", 0, f"{n}x: {text}")
    budget = 150 + 100 * max(criteria, 1)
    lines = size(changes)
    if lines > budget:
        flag("huge_diff", "", 0, f"{lines} lines changed for {criteria or 1} acceptance criteria (budget {budget})")
    # cap repeated low-weight flags so one noisy file doesn't zero the score
    seen: Counter[str] = Counter()
    penalty = 0
    for f in flags:
        seen[f["code"]] += 1
        if seen[f["code"]] <= 3:
            penalty += f["weight"]
    return {"score": max(0, 100 - penalty), "flags": flags, "lines_changed": lines,
            "files": len(changes), "code_files": sum(1 for c in changes if is_code(c["path"]))}
