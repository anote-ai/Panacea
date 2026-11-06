"""The one-month trial hire, with a human in the loop.

1. **Start**: pick the role it fills; it comes with default goals for that role.
2. **Week one**: agree on the goals (editable for the first ``GOAL_LOCK_DAYS``
   days, then locked so the trial is judged on what was agreed).
3. **Every week**: a progress report from the scorecard, measured from the
   trial's start, by email and push, saved on the trial.
4. **Day 30**: the end-of-trial report. Each goal is met or not, and the owner
   decides: **convert** to a paid plan, **extend** once by 14 days, or **cancel**.

An **Ourogen operator** (listed in ``COWORKER_OPERATOR_EMAILS``, signed in with
a verified Google or Microsoft address) sees every active trial: progress,
flagged work waiting on the customer, failed runs. Operators can leave a note,
which is logged on the customer's activity and sent to them. They can't approve
or send anything for the customer; approvals stay with the customer.

What happens when goals aren't met (refund or extension) is set out in
``GUARANTEE``. It's shown as-is and needs legal review before launch.
"""
from __future__ import annotations

import os
from datetime import timedelta
from typing import Any

from coworker import scorecard
from coworker.store import Store, iso, parse_iso, utcnow

TRIAL_DAYS = 30
GOAL_LOCK_DAYS = 7
EXTENSION_DAYS = 14
OPEN = ("active", "extended")

GUARANTEE = ("If the goals you agreed on in week one aren't met by day 30, you can extend the trial once by 14 days "
             "at no cost, or end it and pay nothing. (Draft terms: pending legal review.)")

# Goal metrics: a path into the scorecard, how to read it, and its label.
METRICS: dict[str, dict[str, str]] = {
    "totalOutput": {"label": "Pieces of work done", "kind": "count"},
    "output.prsMerged": {"label": "Pull requests merged", "kind": "count"},
    "output.prsOpened": {"label": "Pull requests opened", "kind": "count"},
    "output.prsReviewed": {"label": "Pull requests reviewed", "kind": "count"},
    "output.ticketsShipped": {"label": "Tickets shipped", "kind": "count"},
    "output.emails": {"label": "Emails handled", "kind": "count"},
    "output.meetings": {"label": "Meetings covered", "kind": "count"},
    "output.docsWritten": {"label": "Docs written", "kind": "count"},
    "output.taskRuns": {"label": "Scheduled tasks run", "kind": "count"},
    "quality.acceptance": {"label": "Approved without edits", "kind": "ratio"},
    "quality.engineerPassRate": {"label": "Engineer runs passing tests", "kind": "ratio"},
    "quality.avgSlopScore": {"label": "Average slop score", "kind": "score"},
    "hoursSaved": {"label": "Hours saved (estimate)", "kind": "count"},
}

DEFAULT_GOALS: dict[str, list[dict[str, Any]]] = {
    "engineering": [{"metric": "output.prsOpened", "target": 12}, {"metric": "quality.engineerPassRate", "target": 0.8},
                    {"metric": "quality.avgSlopScore", "target": 80}],
    "sales": [{"metric": "output.emails", "target": 150}, {"metric": "output.meetings", "target": 8},
              {"metric": "quality.acceptance", "target": 0.7}],
    "marketing": [{"metric": "output.docsWritten", "target": 12}, {"metric": "totalOutput", "target": 40},
                  {"metric": "quality.acceptance", "target": 0.6}],
    "healthcare": [{"metric": "output.emails", "target": 200}, {"metric": "output.taskRuns", "target": 20},
                   {"metric": "quality.acceptance", "target": 0.8}],
    "operations": [{"metric": "totalOutput", "target": 100}, {"metric": "quality.acceptance", "target": 0.7}],
    "assistant": [{"metric": "output.emails", "target": 150}, {"metric": "hoursSaved", "target": 20}],
}


class TrialError(Exception):
    def __init__(self, message: str, code: str = "bad_request") -> None:
        super().__init__(message)
        self.code = code


def current(store: Store, user_id: int) -> dict[str, Any] | None:
    return store.one("SELECT * FROM cw_trials WHERE user_id = %s ORDER BY id DESC LIMIT 1", (user_id,))


def _clean_goals(goals: list[dict[str, Any]]) -> list[dict[str, Any]]:
    clean = []
    for g in goals[:8]:
        metric = str(g.get("metric", ""))
        if metric not in METRICS:
            raise TrialError(f"Unknown goal metric '{metric}'")
        try:
            target = float(g.get("target"))  # type: ignore[arg-type]
        except (TypeError, ValueError) as exc:
            raise TrialError(f"Give '{METRICS[metric]['label']}' a number as its target") from exc
        if target <= 0 or (METRICS[metric]["kind"] == "ratio" and target > 1):
            raise TrialError(f"'{METRICS[metric]['label']}' needs a target above 0 (ratios are 0–1)")
        clean.append({"metric": metric, "target": target, "label": METRICS[metric]["label"]})
    if not clean:
        raise TrialError("Agree on at least one goal")
    return clean


def start(store: Store, user_id: int, role: str, goals: list[dict[str, Any]] | None = None,
          approver: str = "") -> dict[str, Any]:
    if role not in DEFAULT_GOALS:
        raise TrialError(f"Pick a role: {', '.join(DEFAULT_GOALS)}")
    existing = current(store, user_id)
    if existing and existing["status"] in OPEN:
        raise TrialError("A trial is already running", "conflict")
    coworker = store.get_coworker(user_id)
    if not coworker:
        raise TrialError("Set up your coworker first", "not_found")
    now = utcnow()
    trial_id = store.insert("cw_trials", {
        "user_id": user_id, "role": role, "status": "active", "started_at": iso(now),
        "ends_at": iso(now + timedelta(days=TRIAL_DAYS)), "goals": _clean_goals(goals or DEFAULT_GOALS[role]),
        "approver": approver.strip()[:255] or coworker.get("owner_email", ""), "reports": [], "outcome": {},
        "created_at": iso(now), "updated_at": iso(now)})
    store.update_coworker(user_id, settings={**(coworker.get("settings") or {}), "role": role})
    store.log(user_id, "trial", f"Started a {TRIAL_DAYS}-day trial as {scorecard.ROLE_LABELS.get(role, role)}",
              {"trial_id": trial_id})
    out = store.get("cw_trials", trial_id, user_id)
    assert out is not None
    return out


def _day(trial: dict[str, Any]) -> int:
    started = parse_iso(trial["started_at"]) or utcnow()
    return max(0, (utcnow() - started).days)


def update_goals(store: Store, user_id: int, goals: list[dict[str, Any]]) -> dict[str, Any]:
    trial = current(store, user_id)
    if not trial or trial["status"] not in OPEN:
        raise TrialError("No trial is running", "not_found")
    if _day(trial) >= GOAL_LOCK_DAYS:
        raise TrialError("Goals are locked after the first week, so the trial is judged on what was agreed", "conflict")
    store.update("cw_trials", trial["id"], user_id, {"goals": _clean_goals(goals), "updated_at": iso()})
    store.log(user_id, "trial", "Updated the trial goals")
    fresh = current(store, user_id)
    assert fresh is not None
    return fresh


def _value(card: dict[str, Any], metric: str) -> float | None:
    node: Any = card
    for part in metric.split("."):
        node = node.get(part) if isinstance(node, dict) else None
    return None if node is None else float(node)


def progress(store: Store, user_id: int, trial: dict[str, Any]) -> dict[str, Any]:
    """Each goal against the scorecard since the trial started, and whether it's on track."""
    days_in = max(1, min(_day(trial) or 1, TRIAL_DAYS + EXTENSION_DAYS))
    total_days = TRIAL_DAYS + (EXTENSION_DAYS if trial["status"] == "extended" or (trial.get("outcome") or {}).get("extended") else 0)
    card = scorecard.card(store, user_id, days_in)
    goals = []
    for g in trial.get("goals") or []:
        actual = _value(card, g["metric"])
        kind = METRICS[g["metric"]]["kind"]
        if kind == "count":
            expected = g["target"] * min(days_in / total_days, 1)
            on_track = actual is not None and actual >= expected
        else:
            on_track = actual is not None and actual >= g["target"]
        goals.append({**g, "actual": actual, "met": actual is not None and actual >= g["target"], "onTrack": on_track})
    return {"day": _day(trial), "of": total_days, "goals": goals, "met": sum(1 for g in goals if g["met"]),
            "scorecard": {"totalOutput": card["totalOutput"], "cost": card["cost"], "vsHire": card["vsHire"],
                          "humanAttentionHours": card["humanAttentionHours"], "quality": card["quality"]}}


def _render(trial: dict[str, Any], prog: dict[str, Any], final: bool) -> str:
    vs = prog["scorecard"]["vsHire"]
    head = "End-of-trial report" if final else f"Trial week {max(1, prog['day'] // 7)} report"
    lines = [f"{head}: day {prog['day']} of {prog['of']}.", ""]
    for g in prog["goals"]:
        actual = "—" if g["actual"] is None else (f"{g['actual']:.0%}" if METRICS[g["metric"]]["kind"] == "ratio"
                                                  else f"{g['actual']:g}")
        target = f"{g['target']:.0%}" if METRICS[g["metric"]]["kind"] == "ratio" else f"{g['target']:g}"
        state = "met" if g["met"] else ("on track" if g["onTrack"] else "behind")
        lines.append(f"- {g['label']}: {actual} of {target} ({state})")
    lines += ["", f"Work done: {prog['scorecard']['totalOutput']}. Your attention: about "
              f"{prog['scorecard']['humanAttentionHours']:g} hours.",
              f"Cost so far: ${prog['scorecard']['cost']['totalUsd']:,.2f}, vs about ${vs['hireCostUsd']:,.0f} for a "
              f"{vs['roleLabel'].lower()} over the same time (benchmark)."]
    if final:
        lines += ["", f"{prog['met']} of {len(prog['goals'])} goals met.", GUARANTEE,
                  "Decide in Coworker → Trial: convert, extend, or cancel."]
    return "\n".join(lines)


def tick(store: Store, user_id: int) -> str:
    """Send the weekly report once per trial week, and the end-of-trial report on day 30. Returns what was sent."""
    trial = current(store, user_id)
    if not trial or trial["status"] not in OPEN:
        return ""
    ends = parse_iso(trial["ends_at"]) or utcnow()
    final = utcnow() >= ends
    week = _day(trial) // 7
    key = f"final:{trial['ends_at']}" if final else f"week:{week}"
    reports = list(trial.get("reports") or [])
    if (not final and week == 0) or any(r.get("key") == key for r in reports):
        return ""
    prog = progress(store, user_id, trial)
    body = _render(trial, prog, final)
    from coworker import notify, push

    subject = "Your trial: final report" if final else f"Your trial: week {week}"
    push.send(store, user_id, subject, body.splitlines()[0], {"url": "/app/coworker/trial"})
    channel = notify.deliver(store, user_id, subject, body)
    reports.append({"key": key, "week": week, "at": iso(), "final": final, "met": prog["met"], "goals": prog["goals"],
                    "channel": channel})
    values: dict[str, Any] = {"reports": reports, "updated_at": iso()}
    if final:
        values["status"] = "ended"
        values["outcome"] = {**(trial.get("outcome") or {}), "met": prog["met"], "of": len(prog["goals"])}
    store.update("cw_trials", trial["id"], user_id, values)
    store.log(user_id, "trial", subject, {"trial_id": trial["id"], "met": prog["met"]})
    return "final" if final else f"week-{week}"


def decide(store: Store, user_id: int, choice: str, plan: str = "coworker") -> dict[str, Any]:
    """After the trial: ``convert`` (to a paid plan), ``extend`` (once, 14 days) or ``cancel``."""
    trial = current(store, user_id)
    if not trial:
        raise TrialError("No trial", "not_found")
    outcome = dict(trial.get("outcome") or {})
    if choice == "extend":
        if outcome.get("extended"):
            raise TrialError("The trial can be extended once", "conflict")
        ends = (parse_iso(trial["ends_at"]) or utcnow()) if trial["status"] in OPEN else utcnow()
        outcome["extended"] = True
        store.update("cw_trials", trial["id"], user_id, {"status": "extended", "outcome": outcome,
                                                         "ends_at": iso(ends + timedelta(days=EXTENSION_DAYS)),
                                                         "updated_at": iso()})
        store.log(user_id, "trial", f"Extended the trial by {EXTENSION_DAYS} days")
    elif choice == "cancel":
        store.update("cw_trials", trial["id"], user_id, {"status": "cancelled", "outcome": {**outcome, "decision": "cancel"},
                                                         "updated_at": iso()})
        store.log(user_id, "trial", "Ended the trial")
    elif choice == "convert":
        from coworker import billing

        if plan not in billing.PLANS or not billing.PLANS[plan]["price_usd"]:
            raise TrialError("Pick a paid plan")
        store.update("cw_trials", trial["id"], user_id, {"status": "converted",
                                                         "outcome": {**outcome, "decision": "convert", "plan": plan},
                                                         "updated_at": iso()})
        store.log(user_id, "trial", f"Converted the trial to {billing.PLANS[plan]['name']}")
    else:
        raise TrialError("Choose convert, extend, or cancel")
    fresh = current(store, user_id)
    assert fresh is not None
    return fresh


# -- operators ---------------------------------------------------------------------------

def is_operator(store: Store, user_id: int) -> bool:
    from coworker import identity

    operators = {e.strip().lower() for e in os.environ.get("COWORKER_OPERATOR_EMAILS", "").split(",") if e.strip()}
    return bool(operators & identity.verified_emails(store, user_id))


def flagged(store: Store, user_id: int) -> dict[str, Any]:
    """What needs a human: flagged actions waiting on the customer, failed actions and runs, escalated reviews."""
    waiting = store.query("SELECT id, type, title, risk, created_at FROM cw_actions WHERE user_id = %s AND status = 'proposed' "
                          "ORDER BY id DESC LIMIT 50", (user_id,))
    failed = store.query("SELECT id, type, title, error, created_at FROM cw_actions WHERE user_id = %s AND status = 'failed' "
                         "ORDER BY id DESC LIMIT 20", (user_id,))
    runs = store.query("SELECT id, title, status, error, created_at FROM cw_eng_runs WHERE user_id = %s "
                       "AND status IN ('failed', 'needs_model') ORDER BY id DESC LIMIT 20", (user_id,))
    reviews = store.query("SELECT id, repo, number, created_at FROM cw_reviews WHERE user_id = %s AND escalate = 1 "
                          "ORDER BY id DESC LIMIT 20", (user_id,))
    return {"waiting": [a for a in waiting if a.get("risk")], "waitingTotal": len(waiting), "failedActions": failed,
            "failedRuns": runs, "escalatedReviews": reviews}


def operator_overview(store: Store) -> list[dict[str, Any]]:
    rows = store.query("SELECT * FROM cw_trials WHERE status IN ('active', 'extended', 'ended') ORDER BY id DESC LIMIT 200")
    out = []
    for t in rows:
        coworker = store.get_coworker(int(t["user_id"])) or {}
        prog = progress(store, int(t["user_id"]), t)
        flags = flagged(store, int(t["user_id"]))
        out.append({**serialize(t), "owner": coworker.get("owner_email", ""), "progress": prog,
                    "flags": {"waiting": len(flags["waiting"]), "failed": len(flags["failedActions"]) + len(flags["failedRuns"]),
                              "escalatedReviews": len(flags["escalatedReviews"])}})
    return out


def operator_note(store: Store, operator_id: int, trial_id: int, text: str) -> dict[str, Any]:
    trial = store.get("cw_trials", trial_id)
    if not trial:
        raise TrialError("No such trial", "not_found")
    text = text.strip()[:2000]
    if not text:
        raise TrialError("Write a note")
    user_id = int(trial["user_id"])
    store.log(user_id, "operator", f"Note from your Ourogen operator: {text}", {"trial_id": trial_id, "operator": operator_id})
    from coworker import notify

    notify.deliver(store, user_id, "A note from your Ourogen operator", text)
    return {"ok": True}


def serialize(trial: dict[str, Any]) -> dict[str, Any]:
    return {"id": trial["id"], "role": trial["role"], "roleLabel": scorecard.ROLE_LABELS.get(trial["role"], trial["role"]),
            "status": trial["status"], "startedAt": trial["started_at"], "endsAt": trial["ends_at"],
            "goals": trial.get("goals") or [], "approver": trial.get("approver") or "",
            "reports": trial.get("reports") or [], "outcome": trial.get("outcome") or {},
            "goalsLocked": _day(trial) >= GOAL_LOCK_DAYS, "guarantee": GUARANTEE}
