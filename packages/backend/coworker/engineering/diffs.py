"""Changes as the reviewer and slop checks see them.

A *change* is ``{"path", "status", "added": [(line, text)], "removed": [text]}``,
built either from a GitHub unified patch or from old/new file contents.
"""
from __future__ import annotations

import difflib
import re
from typing import Any

HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")
TEST_PATH = re.compile(r"(^|/)(tests?|__tests__|spec)/|(^|/)test_[^/]+$|_test\.\w+$|\.(test|spec)\.\w+$")
CODE_EXT = re.compile(r"\.(py|ts|tsx|js|jsx|go|rs|java|kt|rb|cs|php|scala|swift)$")


def from_patch(path: str, patch: str, status: str = "modified") -> dict[str, Any]:
    added: list[tuple[int, str]] = []
    removed: list[str] = []
    line = 0
    for raw in (patch or "").splitlines():
        m = HUNK.match(raw)
        if m:
            line = int(m.group(1))
            continue
        if raw.startswith("+") and not raw.startswith("+++"):
            added.append((line, raw[1:]))
            line += 1
        elif raw.startswith("-") and not raw.startswith("---"):
            removed.append(raw[1:])
        elif raw.startswith("\\"):
            continue
        else:
            line += 1
    return {"path": path, "status": status, "added": added, "removed": removed}


def unified(path: str, old: str | None, new: str | None) -> str:
    return "".join(difflib.unified_diff((old or "").splitlines(keepends=True), (new or "").splitlines(keepends=True),
                                        fromfile=f"a/{path}", tofile=f"b/{path}"))


def from_contents(path: str, old: str | None, new: str | None) -> dict[str, Any]:
    status = "added" if old is None else "removed" if new is None else "modified"
    change = from_patch(path, unified(path, old, new), status)
    change["patch"] = unified(path, old, new)
    return change


def from_github_files(files: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{**from_patch(f.get("path", ""), f.get("patch", ""), f.get("status", "modified")), "patch": f.get("patch", "")}
            for f in files]


def is_test(path: str) -> bool:
    return bool(TEST_PATH.search(path))


def is_code(path: str) -> bool:
    return bool(CODE_EXT.search(path))


def size(changes: list[dict[str, Any]]) -> int:
    return sum(len(c["added"]) + len(c["removed"]) for c in changes)
