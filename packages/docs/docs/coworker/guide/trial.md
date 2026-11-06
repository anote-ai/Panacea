# The one-month trial

Hire your AI the way you'd hire a person: agree on what success looks like, watch the numbers every week, and decide after a month. **Coworker → Trial.**

## How it works

1. **Start.** Pick the seat it fills: software engineer, SDR, marketer, front-office admin, operations admin, or executive assistant. Each comes with default goals for day 30, which you can change.
2. **Week one.** Agree on the goals. They lock after day 7, so the trial is judged on what you agreed.
3. **Every week.** A progress report by email and push: each goal (met, on track, or behind), work done, your attention, and cost next to a hire for the same role. Counts are judged against a pro-rated target, so "on track" in week 2 means at least half of the way to a 30-day target by day 15.
4. **Day 30.** The end-of-trial report says which goals were met. Then you decide:
   - **Keep it**: move to a paid plan (Stripe Checkout, or a plan swap if you already subscribe).
   - **Extend 14 days**, once.
   - **End it.**

Goals are measured with the [scorecard](scorecard.md), from the day the trial started.

| Goal metric | Example target |
|---|---|
| Pull requests opened / merged / reviewed | 12 opened in 30 days |
| Tickets shipped | 8 |
| Engineer runs passing tests | 0.8 (80%) |
| Average slop score | 80 |
| Emails handled, meetings covered, docs written, scheduled tasks run | 150 emails |
| Approved without edits | 0.7 (70%) |
| Pieces of work done, hours saved (estimate) | 100 |

## The human in the loop

You approve what matters, as always. During a trial, an **Ourogen operator** also watches your AI's work:

- Operators see every running trial: progress on each goal, work flagged and waiting on you, failed actions and engineer runs, and escalated code reviews.
- They can send you a note. It shows in your activity log and arrives by email.
- They can't approve, send, or change anything for you.

Operators are the people listed in `COWORKER_OPERATOR_EMAILS`, signed in with a verified Google or Microsoft address. They see the operator view at the bottom of the Trial tab.

## If the goals aren't met

> If the goals you agreed on in week one aren't met by day 30, you can extend the trial once by 14 days at no cost, or end it and pay nothing.

These are **draft terms, pending legal review** (tracked with the launch legal review). Change `GUARANTEE` in `coworker/trial.py` once they're final.

## API

`GET /trial`, `POST /trial` (`{"role", "goals", "approver"}`), `PUT /trial/goals`, `POST /trial/decide` (`{"choice": "convert" | "extend" | "cancel", "plan"}`); operators: `GET /operator/trials`, `GET /operator/trials/<id>`, `POST /operator/trials/<id>/notes`.
