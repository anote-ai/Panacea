# Code evals

How we know the AI engineer, the code reviewer, and the slop checks are good enough to trust, and that they stay that way.

```bash
cd packages/backend
python -m coworker.evals.run
```

The code suites run with the coworker's other evals, offline, on every push. CI blocks the merge if any score drops below its threshold.

| Suite | What it measures | Threshold |
|---|---|---|
| `engineer_tasks` | Specs with **hidden tests** on the demo repo. The engineer never sees them; a task passes when they pass on its output. | 100% |
| `reviewer_recall` | Labeled buggy changes: does the reviewer raise each expected finding? | 90% |
| `reviewer_precision` | Of the high/medium findings it raises on labeled cases, how many were expected? | 90% |
| `slop_flags` | Labeled changes: the slop flags that must, and must not, appear | 90% |
| `pack_lift` | With your knowledge pack, the reviewer catches more of your own past review concerns than without it | 100% |

Offline, `engineer_tasks` uses the demo's scripted solution, so it checks the harness (sandbox, hidden tests, PR payload). With a model configured, the same suite measures the model.

Add a case to `coworker/evals/code.py` whenever you fix a reviewer or slop bug, so it stays fixed.

## Slop checks

Every PR the AI engineer proposes, and every reviewed PR, gets a **slop score** from 0 to 100 (100 is clean). Each flag costs points (a repeated flag counts at most 3 times):

| Flag | Points | What it catches |
|---|---|---|
| `skipped_test` | 25 | `@pytest.mark.skip`, `it.skip(`, `xit(` … |
| `weakened_test` | 20 | Assertions removed from a test |
| `huge_diff` | 15 | More than 150 lines + 100 per acceptance criterion |
| `unknown_import` | 15 | A Python import that isn't in the repo, its requirements, or the standard library (an invented API?) |
| `duplicated_block` | 8 | The same long line added 3+ times |
| `dead_code` | 6 | A new function nothing calls |
| `todo_left` | 5 | `TODO`, `FIXME`, `XXX`, `HACK` |
| `debug_left` | 5 | `print(`, `console.log(`, `debugger`, `breakpoint()` outside tests |
| `bare_except` | 5 | Swallowing every exception |
| `restating_comment` | 3 | A comment that only repeats the next line |

**Autonomy gate:** a PR whose score is below your minimum (default 70) always waits for your approval.

## Human agreement

Every approval records whether you approved it as-is, edited it, or rejected it, and earned autonomy already uses the streak of unedited approvals. A human-agreement score per AI (how often its PRs are accepted without changes) comes with the output scorecard ([#449](https://github.com/anote-ai/Panacea/issues/449)).

Code: `coworker/evals/code.py`, `coworker/engineering/slop.py`.
