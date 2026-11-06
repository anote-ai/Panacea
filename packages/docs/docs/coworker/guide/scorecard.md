# The scorecard

**Coworker → Scorecard** answers one question: how much work did your AI get done, how good was it, and what did it cost? Pick today, 7 days, or 30 days, or download it as CSV.

| Section | What it shows |
|---|---|
| **Work done** | Everything it shipped in the range, per day; your attention (estimate); hours it was active; hours saved (estimate) |
| **What it shipped** | PRs opened, merged and reviewed; engineer runs; tickets shipped; emails, Slack posts, invites, CRM updates; meetings covered; briefs; scheduled task runs |
| **Quality** | Approved without edits, edits per approval, actions undone, engineer runs passing their tests, average slop score |
| **Cost, next to a hire** | Your plan (prorated) plus model cost, against a salary benchmark for the role over the same period, and the value of the hours saved at that role's hourly cost |
| **Latest eval scores** | The offline eval suites from CI |

## Estimates

- **Your attention** counts 30 seconds per approval, 2 minutes per edit, and 1 minute per rejection or call takeover.
- **Hours saved** is minutes per task times tasks done, plus call time.
- **Salary benchmarks** are typical fully loaded costs: engineer $200k, SDR $110k, marketer $120k, operations admin $70k, front-office admin $60k, executive assistant $80k. Operators can change them with `COWORKER_ROLE_SALARIES` (JSON, e.g. `{"engineering": 180000}`).

Pick the role it fills in **Settings → Identity & preferences**. Left unset, it's an engineer once it has done engineering work, otherwise an SDR.

PRs count as merged once GitHub says so. The scorecard checks your open engineer PRs each time you open it.

## Weekly report

Monday's weekly report now starts with the week's scorecard: work done, your attention, PRs opened, merged and reviewed, and cost next to a hire.

## Team

Organization admins get every member's scorecard and team totals: `GET /api/coworker/team/scorecard?days=30`.

## API

`GET /api/coworker/scorecard?days=7` (JSON) or `?format=csv`; `GET /api/coworker/team/scorecard?days=7` (admins).
