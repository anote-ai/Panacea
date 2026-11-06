"""Evals for the AI engineer, the code reviewer, and the slop checks.

* ``engineer_tasks``: specs with hidden tests on the demo repo. The engineer never
  sees the hidden tests; a task passes when they pass on its output.
  (Offline, the demo uses its scripted solution, so this checks the harness.
  With a model, it measures the model.)
* ``reviewer_recall`` / ``reviewer_precision``: labeled buggy and clean changes.
* ``slop_flags``: labeled changes with the slop flags they must (and must not) raise.
* ``pack_lift``: the reviewer, with the owner's knowledge pack, catches more of
  the owner's own historical review concerns than without it.
"""
from __future__ import annotations

import time
from typing import Any

from coworker import knowledge_pack
from coworker.connectors import devtools
from coworker.engineering import review, runs, sandbox, slop
from coworker.engineering.demo import DEMO_HIDDEN_TESTS, DEMO_REVIEW_PATCH
from coworker.engineering.diffs import from_contents, from_github_files
from coworker.store import Store

ENGINEER_TASKS: list[dict[str, Any]] = [
    {"name": "ACME-142 annual billing", "source": "jira:ACME-142", "hidden_tests": {"tests/test_hidden_annual.py": DEMO_HIDDEN_TESTS}},
]


def _c(path: str, old: str | None, new: str) -> dict[str, Any]:
    return from_contents(path, old, new)


# (name, changes, checks the reviewer must raise)
REVIEW_CASES: list[tuple[str, list[dict[str, Any]], set[str]]] = [
    ("teammate PR #37", from_github_files(DEMO_REVIEW_PATCH), {"money_decimal", "no_skipped_tests", "specific_except"}),
    ("committed secret", [_c("app/config.py", "", 'API_KEY = "sk-ant-api03-abcdefghijklmnopqrstuv"\n'),
                          _c("tests/test_config.py", "", "def test_ok():\n    assert True\n")], {"secret"}),
    ("code without tests", [_c("app/fees.py", "", "from decimal import Decimal\n\n\ndef late_fee(days):\n"
                                                  "    return Decimal('5') * days\n")], {"tests"}),
    ("weakened test", [_c("tests/test_fees.py", "def test_fee():\n    assert late_fee(2) == 10\n    assert late_fee(0) == 0\n",
                          "def test_fee():\n    late_fee(2)\n")], {"weakened_test"}),
    ("debug print", [_c("app/fees.py", "def f():\n    return 1\n", "def f():\n    print('here')\n    return 1\n"),
                     _c("tests/test_f.py", "", "def test_f():\n    assert f() == 1\n")], {"debug_left"}),
    ("clean change", [_c("app/fees.py", "", "from decimal import Decimal\n\n\ndef late_fee(day_count: int) -> Decimal:\n"
                                            "    return Decimal('5') * day_count\n"),
                      _c("tests/test_fees.py", "", "from decimal import Decimal\n\nfrom app.fees import late_fee\n\n\n"
                                                   "def test_late_fee():\n    assert late_fee(2) == Decimal('10')\n"),
                      _c("README.md", "# acme\n", "# acme\n\nLate fees are $5 a day.\n")], set()),
]

# (name, changes, flags that must appear, flags that must not)
SLOP_CASES: list[tuple[str, list[dict[str, Any]], set[str], set[str]]] = [
    ("skipped test", [_c("tests/test_a.py", "def test_a():\n    assert 1\n",
                         "import pytest\n\n\n@pytest.mark.skip\ndef test_a():\n    assert 1\n")], {"skipped_test"}, set()),
    ("weakened test", [_c("tests/test_a.py", "def test_a():\n    assert f() == 2\n", "def test_a():\n    f()\n")],
     {"weakened_test"}, set()),
    ("invented import", [_c("app/x.py", "", "import fastmoneyz\n\n\ndef run():\n    return fastmoneyz.go()\n\n\nrun()\n")],
     {"unknown_import"}, set()),
    ("restating comment", [_c("app/x.py", "", "def total(items):\n    # return the sum of items\n    return sum(items)\n\n\n"
                                              "total([1])\n")], {"restating_comment"}, set()),
    ("todo left", [_c("app/x.py", "", "def f():\n    return 1  # TODO handle errors\n\n\nf()\n")], {"todo_left"}, set()),
    ("dead code", [_c("app/x.py", "", "def helper_nobody_calls():\n    return 1\n")], {"dead_code"}, set()),
    ("huge diff", [_c("app/big.py", "", "".join(f"VALUE_{i} = {i}\n" for i in range(400)))], {"huge_diff"}, set()),
    ("clean", [_c("app/x.py", "", "from decimal import Decimal\n\n\ndef fee(day_count: int) -> Decimal:\n"
                                  "    return Decimal('5') * day_count\n"),
               _c("tests/test_x.py", "", "from app.x import fee\n\n\ndef test_fee():\n    assert fee(1) == 5\n")],
     set(), {"skipped_test", "weakened_test", "unknown_import", "todo_left", "debug_left", "huge_diff", "dead_code"}),
]


def engineer_tasks(store: Store) -> dict[str, Any]:
    misses = []
    durations = []
    for task in ENGINEER_TASKS:
        started = time.monotonic()
        run = runs.create(store, 1, source=task["source"])
        run = runs.plan(store, 1, run["id"])
        run = runs.start(store, 1, run["id"])
        durations.append(time.monotonic() - started)
        if run["status"] not in ("ready", "pr_opened"):
            misses.append({"case": task["name"], "expected": "ready", "got": f"{run['status']}: {run.get('error', '')}"})
            continue
        action = store.get("cw_actions", run["action_id"], 1) or {}
        files = {f["path"]: (None if f.get("delete") else f["content"]) for f in (action.get("payload") or {}).get("files") or []}
        checks = sandbox.run(run["repo"], files, extra_files=task["hidden_tests"])
        if not checks.get("passed"):
            misses.append({"case": task["name"], "expected": "hidden tests pass", "got": checks.get("output", "")[-300:]})
    n = len(ENGINEER_TASKS)
    return {"score": 1 - len(misses) / n, "n": n, "misses": misses,
            "seconds": round(sum(durations) / max(len(durations), 1), 2)}


def _pack(store: Store) -> dict[str, Any]:
    return knowledge_pack.current(store, 1)


def reviewer_recall(store: Store) -> dict[str, Any]:
    pack = _pack(store)
    expected = sum(len(want) for _, _, want in REVIEW_CASES)
    misses = []
    for name, changes, want in REVIEW_CASES:
        got = {f["check"] for f in review.review_changes(changes, pack=pack, use_model=False)["findings"]}
        for check in want - got:
            misses.append({"case": name, "expected": check, "got": sorted(got)})
    return {"score": 1 - len(misses) / max(expected, 1), "n": expected, "misses": misses}


def reviewer_precision(store: Store) -> dict[str, Any]:
    """Of the high/medium findings raised on labeled cases, how many were expected."""
    pack = _pack(store)
    raised, misses = 0, []
    for name, changes, want in REVIEW_CASES:
        for f in review.review_changes(changes, pack=pack, use_model=False)["findings"]:
            if f["severity"] == "low":
                continue
            raised += 1
            if f["check"] not in want:
                misses.append({"case": name, "expected": sorted(want), "got": f["check"]})
    return {"score": 1 - len(misses) / max(raised, 1), "n": raised, "misses": misses}


def slop_flags(store: Store) -> dict[str, Any]:
    misses = []
    for name, changes, must, must_not in SLOP_CASES:
        got = {f["code"] for f in slop.report(changes, criteria=1)["flags"]}
        misses += [{"case": name, "expected": code, "got": sorted(got)} for code in must - got]
        misses += [{"case": name, "expected": f"no {code}", "got": sorted(got)} for code in must_not & got]
    n = sum(len(m) + len(x) for _, _, m, x in SLOP_CASES)
    return {"score": 1 - len(misses) / n, "n": n, "misses": misses}


def pack_lift(store: Store) -> dict[str, Any]:
    """The owner's past review concerns (from the pack's rules) that the reviewer catches on PR #37."""
    pack = _pack(store)
    concerns = {r["check"] for r in pack.get("style_rules") or [] if r.get("check")}
    changes = from_github_files(DEMO_REVIEW_PATCH)
    with_pack = {f["check"] for f in review.review_changes(changes, pack=pack, use_model=False)["findings"]} & concerns
    without = {f["check"] for f in review.review_changes(changes, pack={}, use_model=False)["findings"]} & concerns
    misses = [] if len(with_pack) > len(without) else [{"case": "PR #37", "expected": "more with the pack",
                                                         "got": f"{len(with_pack)} vs {len(without)}"}]
    return {"score": 0.0 if misses else 1.0, "n": 1, "misses": misses,
            "with_pack": sorted(with_pack), "without_pack": sorted(without)}


def seed(store: Store) -> None:
    devtools.ensure_demo(store, 1)


SUITES = {"engineer_tasks": engineer_tasks, "reviewer_recall": reviewer_recall,
          "reviewer_precision": reviewer_precision, "slop_flags": slop_flags, "pack_lift": pack_lift}
THRESHOLDS = {"engineer_tasks": 1.0, "reviewer_recall": 0.9, "reviewer_precision": 0.9, "slop_flags": 0.9,
              "pack_lift": 1.0}
