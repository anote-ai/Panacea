"""The output scorecard: work done per unit of time, per AI and per team.

``card(store, user_id, days)`` answers "what did my AI get done, how good was
it, what did it cost, and how does that compare with a person in the role?":

* **Output**: PRs opened and merged, code reviews, engineer runs, tickets
  shipped (runs started from a ticket whose PR was opened), emails, Slack posts,
  invites, CRM updates, meetings covered, briefs, scheduled task runs.
* **Rates**: per day, per hour of human attention (an estimate from approvals,
  edits and call interventions), and per dollar (the plan, prorated, plus
  model cost).
* **Quality**: acceptance without edits, edits per approval, reverts (undone
  actions), engineer review pass rate, average slop score, and the latest
  offline eval scores.
* **Versus a hire**: the AI's cost for the period against a salary benchmark
  for the role, and hours of work done valued at that role's hourly cost.
  Benchmarks are defaults, overridable with ``COWORKER_ROLE_SALARIES`` (JSON).

Everything that's an estimate is labeled as one.
"""
from __future__ import annotations

import csv
import io
import json
import os
from datetime import timedelta
from typing import Any

from coworker import metrics
from coworker.store import Store, iso, parse_iso, utcnow

# Fully loaded annual cost, USD. Overridable; shown as a benchmark, never as a fact about the customer.
ROLE_SALARIES = {"engineering": 200_000, "sales": 110_000, "marketing": 120_000, "operations": 70_000,
                 "healthcare": 60_000, "assistant": 80_000}
ROLE_LABELS = {"engineering": "Software engineer", "sales": "SDR", "marketing": "Marketer",
               "operations": "Operations admin", "healthcare": "Front-office admin", "assistant": "Executive assistant"}
WORK_HOURS_PER_MONTH = 160

# Minutes of the owner's attention each kind of touch takes (estimates).
ATTENTION_MINUTES = {"approve": 0.5, "edit": 2.0, "reject": 1.0, "intervention": 1.0}

OUTPUT_TYPES = {
    "email.send": "emails", "slack.post": "slackPosts", "calendar.create": "invites", "crm.update": "crmUpdates",
    "github.pr": "prsOpened", "github.review": "reviewsPosted", "github.comment": "comments",
    "github.issue": "issuesFiled", "jira.issue": "ticketsFiled", "jira.comment": "comments",
    "notion.page": "docsWritten", "mcp.call": "toolCalls",
}


def salaries() -> dict[str, int]:
    try:
        custom = json.loads(os.environ.get("COWORKER_ROLE_SALARIES") or "{}")
    except ValueError:
        custom = {}
    return {**ROLE_SALARIES, **{k: int(v) for k, v in custom.items() if isinstance(v, int | float)}}


def role_for(store: Store, user_id: int) -> str:
    coworker = store.get_coworker(user_id) or {}
    role = str((coworker.get("settings") or {}).get("role") or "")
    if role in salaries():
        return role
    has_code = store.one("SELECT id FROM cw_eng_runs WHERE user_id = %s LIMIT 1", (user_id,))
    return "engineering" if has_code else "sales"


def _plan_cost(store: Store, user_id: int, days: int) -> float:
    from coworker import billing

    plan = billing.PLANS.get(billing.effective_plan(store, user_id)) or {}
    return round(float(plan.get("price_usd") or 0) * days / 30, 2)


def _model_cost(store: Store, user_id: int, since: str) -> float:
    runs = store.one("SELECT COALESCE(SUM(cost_micros), 0) AS c FROM cw_runs WHERE user_id = %s AND created_at >= %s",
                     (user_id, since))
    eng = store.one("SELECT COALESCE(SUM(cost_micros), 0) AS c FROM cw_eng_runs WHERE user_id = %s AND created_at >= %s",
                    (user_id, since))
    return round((int((runs or {}).get("c") or 0) + int((eng or {}).get("c") or 0)) / 1_000_000, 2)


def _active_hours(store: Store, user_id: int, since: str) -> int:
    """Distinct clock hours in which the AI did something (from the activity log)."""
    hours = set()
    for a in store.activity(user_id, limit=20000, since=since):
        if a["kind"] in ("auto_approved", "executed", "engineer", "review", "brief", "run", "notification", "proposed"):
            at = parse_iso(a["created_at"])
            if at:
                hours.add(at.strftime("%Y-%m-%dT%H"))
    return len(hours)


def card(store: Store, user_id: int, days: int = 7) -> dict[str, Any]:
    days = max(1, min(int(days), 365))
    since = iso(utcnow() - timedelta(days=days))
    track = metrics.track_record(store, user_id, days=days)
    output: dict[str, int] = {v: 0 for v in OUTPUT_TYPES.values()}
    for kind, stats in track["byType"].items():
        if kind in OUTPUT_TYPES:
            output[OUTPUT_TYPES[kind]] += int(stats.get("executed") or 0)

    eng = store.query("SELECT status, source, pr, slop, checks, review_id FROM cw_eng_runs WHERE user_id = %s "
                      "AND created_at >= %s", (user_id, since))
    finished = [r for r in eng if r["status"] in ("ready", "pr_opened")]
    output["engineerRuns"] = len(finished)
    output["prsMerged"] = sum(1 for r in eng if (r.get("pr") or {}).get("merged"))
    output["ticketsShipped"] = sum(1 for r in eng if r["status"] == "pr_opened" and (r.get("source") or "").startswith("jira:"))
    reviews = store.query("SELECT findings, escalate FROM cw_reviews WHERE user_id = %s AND source = 'pr' AND created_at >= %s",
                          (user_id, since))
    output["prsReviewed"] = len(reviews)
    output["meetings"] = track["calls"]["count"]
    output["briefs"] = track["briefs"]
    task_runs = store.one("SELECT COUNT(*) AS n FROM cw_runs WHERE user_id = %s AND created_at >= %s AND status = 'done'",
                          (user_id, since))
    output["taskRuns"] = int((task_runs or {}).get("n") or 0)
    total = sum(output.values()) - output["prsMerged"]  # merged PRs were already counted when opened

    # Human attention (estimate)
    decided = track["decided"]
    edited = sum(int(v.get("edited") or 0) for v in track["byType"].values())
    rejected = sum(int(v.get("rejected") or 0) for v in track["byType"].values())
    approved = max(decided - edited - rejected, 0)
    attention_min = (approved * ATTENTION_MINUTES["approve"] + edited * ATTENTION_MINUTES["edit"]
                     + rejected * ATTENTION_MINUTES["reject"] + track["calls"]["interventions"] * ATTENTION_MINUTES["intervention"])
    attention_hours = round(attention_min / 60, 2)

    # Quality
    undone = store.one("SELECT COUNT(*) AS n FROM cw_actions WHERE user_id = %s AND status = 'undone' AND created_at >= %s",
                       (user_id, since))
    passed = [r for r in finished if (r.get("checks") or {}).get("passed") is not False]
    slops = [int((r.get("slop") or {}).get("score") or 0) for r in finished if (r.get("slop") or {}).get("score") is not None]
    quality = {
        "acceptance": track["acceptance"],
        "editsPerApproval": round(edited / decided, 3) if decided else None,
        "reverts": int((undone or {}).get("n") or 0),
        "engineerPassRate": round(len(passed) / len(finished), 3) if finished else None,
        "avgSlopScore": round(sum(slops) / len(slops), 1) if slops else None,
        "evals": latest_evals(),
    }

    # Cost, rates, and the comparison with a hire
    plan_cost = _plan_cost(store, user_id, days)
    model_cost = _model_cost(store, user_id, since)
    cost = round(plan_cost + model_cost, 2)
    role = role_for(store, user_id)
    salary = salaries()[role]
    hire_cost = round(salary / 365 * days, 2)
    hourly = salary / 12 / WORK_HOURS_PER_MONTH
    hours_saved = float(track["hoursSaved"])
    return {
        "days": days,
        "since": since,
        "output": output,
        "totalOutput": total,
        "activeHours": _active_hours(store, user_id, since),
        "humanAttentionHours": attention_hours,
        "rates": {
            "perDay": round(total / days, 2),
            "perHumanHour": round(total / attention_hours, 1) if attention_hours else None,
            "perDollar": round(total / cost, 3) if cost else None,
        },
        "quality": quality,
        "cost": {"planUsd": plan_cost, "modelUsd": model_cost, "totalUsd": cost},
        "hoursSaved": hours_saved,
        "vsHire": {
            "role": role, "roleLabel": ROLE_LABELS.get(role, role.title()), "annualSalaryUsd": salary,
            "hireCostUsd": hire_cost, "aiCostUsd": cost,
            "costRatio": round(cost / hire_cost, 3) if hire_cost else None,
            "workValueUsd": round(hours_saved * hourly, 2),
        },
        "notes": {
            "hoursSaved": track["hoursSavedNote"],
            "humanAttention": "Estimate: 30 seconds per approval, 2 minutes per edit, 1 minute per rejection or call takeover.",
            "vsHire": "Benchmark: a typical fully loaded salary for the role, prorated. Set yours in Settings.",
        },
    }


def latest_evals() -> dict[str, float]:
    path = os.path.join(os.path.dirname(__file__), "evals", "history.jsonl")
    try:
        with open(path) as fh:
            lines = [ln for ln in fh.read().splitlines() if ln.strip()]
        row = json.loads(lines[-1]) if lines else {}
    except (OSError, ValueError):
        return {}
    return {k: v.get("score") for k, v in (row.get("suites") or {}).items()}


def team(store: Store, user_id: int, days: int = 7) -> dict[str, Any] | None:
    """Every active member's card, plus totals. Admins only."""
    from coworker import orgs

    m = orgs.membership(store, user_id)
    if not m or m["role"] != "admin":
        return None
    rows = store.query("SELECT user_id, email FROM cw_org_members WHERE org_id = %s AND status = 'active' "
                       "AND user_id IS NOT NULL ORDER BY id", (m["org_id"],))
    members = []
    for r in rows:
        if store.get_coworker(int(r["user_id"])):
            members.append({"email": r["email"], **card(store, int(r["user_id"]), days)})
    totals = {
        "totalOutput": sum(c["totalOutput"] for c in members),
        "humanAttentionHours": round(sum(c["humanAttentionHours"] for c in members), 2),
        "costUsd": round(sum(c["cost"]["totalUsd"] for c in members), 2),
        "hireCostUsd": round(sum(c["vsHire"]["hireCostUsd"] for c in members), 2),
        "hoursSaved": round(sum(c["hoursSaved"] for c in members), 1),
    }
    return {"days": days, "members": members, "totals": totals}


CSV_FIELDS = ["metric", "value"]


def to_csv(data: dict[str, Any]) -> str:
    rows: list[tuple[str, Any]] = [("days", data["days"]), ("total_output", data["totalOutput"]),
                                   ("active_hours", data["activeHours"]), ("human_attention_hours", data["humanAttentionHours"]),
                                   ("hours_saved_estimate", data["hoursSaved"])]
    rows += [(f"output.{k}", v) for k, v in data["output"].items()]
    rows += [(f"rate.{k}", v) for k, v in data["rates"].items()]
    rows += [(f"quality.{k}", v) for k, v in data["quality"].items() if k != "evals"]
    rows += [(f"eval.{k}", v) for k, v in data["quality"]["evals"].items()]
    rows += [(f"cost.{k}", v) for k, v in data["cost"].items()]
    rows += [(f"vs_hire.{k}", v) for k, v in data["vsHire"].items()]
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(CSV_FIELDS)
    for name, value in rows:
        writer.writerow([name, "" if value is None else value])
    return buf.getvalue()


def refresh_merged(store: Store, user_id: int) -> int:
    """Mark engineer PRs merged on GitHub. Live connections only; returns how many changed."""
    from coworker.connectors import devtools

    client = devtools.live_client(store, user_id, "github")
    if not client:
        return 0
    changed = 0
    for run in store.query("SELECT id, repo, pr FROM cw_eng_runs WHERE user_id = %s AND status = 'pr_opened'", (user_id,)):
        pr = run.get("pr") or {}
        if pr.get("merged") or not str(pr.get("number") or "").isdigit():
            continue
        try:
            body = client.request("GET", f"/repos/{run['repo']}/pulls/{pr['number']}")
        except Exception:  # one bad PR never stops the others
            continue
        if body.get("merged_at"):
            store.update("cw_eng_runs", run["id"], user_id, {"pr": {**pr, "merged": True, "merged_at": body["merged_at"]}})
            changed += 1
    return changed


def weekly_lines(store: Store, user_id: int) -> list[str]:
    """Scorecard lines for the weekly report."""
    c = card(store, user_id, 7)
    o = c["output"]
    lines = [f"Output this week: {c['totalOutput']} pieces of work, about {c['humanAttentionHours']:g} hours of your attention."]
    if o["prsOpened"] or o["prsReviewed"]:
        lines.append(f"Code: {o['prsOpened']} PRs opened, {o['prsMerged']} merged, {o['prsReviewed']} reviewed.")
    lines.append(f"Cost: ${c['cost']['totalUsd']:,.2f} vs about ${c['vsHire']['hireCostUsd']:,.0f} for a "
                 f"{c['vsHire']['roleLabel'].lower()} over the same week (benchmark).")
    return lines
