"""Margin analysis for the plan lineups: does each price cover what users actually cost?

    python -m coworker.pricing            # against COWORKER_DB_URL (run it on production data)
    python -m coworker.pricing --json

For every user with a coworker it measures the last 30 days of variable cost:
model spend (scheduled tasks and engineer runs, metered per call), call
minutes, text-to-speech, and executed actions (rates from ``billing``). It then
prices each plan at the typical (p50) and heavy (p90) user, with the plan's
caps applied, and suggests the largest engineer-run cap that keeps the heavy
user at the target margin.

With no measured engineer runs it falls back to ``COWORKER_COST_PER_ENGINEER_RUN``
(default $1.50), and says so.
"""
from __future__ import annotations

import argparse
import json
import math
import os
from datetime import timedelta
from typing import Any

from coworker import billing
from coworker.store import Store, get_store, iso, utcnow

TARGET_MARGIN = float(os.environ.get("COWORKER_TARGET_MARGIN", "0.6"))


def default_run_cost() -> float:
    return float(os.environ.get("COWORKER_COST_PER_ENGINEER_RUN", "1.50"))


def _percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    k = (len(ordered) - 1) * p
    lo, hi = math.floor(k), math.ceil(k)
    return ordered[lo] + (ordered[hi] - ordered[lo]) * (k - lo)


def user_costs(store: Store, days: int = 30) -> list[dict[str, Any]]:
    since = iso(utcnow() - timedelta(days=days))
    out = []
    for c in store.query("SELECT user_id, plan FROM cw_coworkers"):
        uid = int(c["user_id"])
        usage = store.usage_since(uid, since)
        tasks = store.one("SELECT COALESCE(SUM(cost_micros), 0) AS c FROM cw_runs WHERE user_id = %s AND created_at >= %s",
                          (uid, since))
        eng = store.one("SELECT COUNT(*) AS n, COALESCE(SUM(cost_micros), 0) AS c FROM cw_eng_runs WHERE user_id = %s "
                        "AND created_at >= %s AND status NOT IN ('spec', 'planned')", (uid, since))
        actions = store.one("SELECT COUNT(*) AS n FROM cw_actions WHERE user_id = %s AND status = 'executed' AND created_at >= %s",
                            (uid, since))
        call_min = usage.get("call_seconds", 0) / 60
        base = (int((tasks or {}).get("c") or 0) / 1_000_000 + call_min * billing.COST_PER_CALL_MINUTE
                + usage.get("tts_chars", 0) / 1000 * billing.COST_PER_1K_TTS_CHARS
                + int((actions or {}).get("n") or 0) * billing.COST_PER_ACTION)
        out.append({"userId": uid, "plan": c.get("plan") or "pilot", "baseCostUsd": round(base, 4),
                    "engineerRuns": int((eng or {}).get("n") or 0),
                    "engineerCostUsd": round(int((eng or {}).get("c") or 0) / 1_000_000, 4),
                    "callMinutes": round(call_min, 1)})
    return out


def analyze(store: Store, days: int = 30, target: float = TARGET_MARGIN) -> dict[str, Any]:
    users = user_costs(store, days)
    runs = sum(u["engineerRuns"] for u in users)
    measured = runs > 0 and sum(u["engineerCostUsd"] for u in users) > 0
    run_cost = round(sum(u["engineerCostUsd"] for u in users) / runs, 4) if measured else default_run_cost()
    base = [u["baseCostUsd"] for u in users]
    eng_runs = [u["engineerRuns"] for u in users]
    profiles = {
        "p50": {"baseCostUsd": round(_percentile(base, 0.5), 2), "engineerRuns": round(_percentile(eng_runs, 0.5), 1)},
        "p90": {"baseCostUsd": round(_percentile(base, 0.9), 2), "engineerRuns": round(_percentile(eng_runs, 0.9), 1)},
    }
    plans = []
    for pid in dict.fromkeys(billing.ORDER + billing.ORDER_V3):
        plan = billing.PLANS[pid]
        price = float(plan["price_usd"])
        cap = billing.ENGINEER_RUNS.get(pid)
        row: dict[str, Any] = {"plan": pid, "name": plan["name"], "priceUsd": price, "engineerRunCap": cap,
                               "lineup": "v3" if pid in billing.ORDER_V3 and pid not in billing.ORDER else
                               "both" if pid in billing.ORDER_V3 else "current"}
        for name, prof in profiles.items():
            used = prof["engineerRuns"] if cap is None else min(prof["engineerRuns"], cap)
            cost = prof["baseCostUsd"] + used * run_cost
            row[name] = {"costUsd": round(cost, 2), "marginUsd": round(price - cost, 2),
                         "margin": round((price - cost) / price, 3) if price else None}
        # The worst case the cap allows: a heavy user who uses every run.
        if cap is not None:
            worst = profiles["p90"]["baseCostUsd"] + cap * run_cost
            row["atCap"] = {"costUsd": round(worst, 2), "margin": round((price - worst) / price, 3) if price else None}
        row["suggestedRunCap"] = None
        if price and run_cost:
            room = price * (1 - target) - profiles["p90"]["baseCostUsd"]
            row["suggestedRunCap"] = max(0, math.floor(room / run_cost))
        plans.append(row)
    return {"days": days, "users": len(users), "engineerRunCostUsd": run_cost, "runCostMeasured": measured,
            "targetMargin": target, "profiles": profiles, "plans": plans,
            "note": ("Engineer run cost is measured from metered runs." if measured else
                     f"No metered engineer runs yet; assuming ${run_cost:.2f} per run (COWORKER_COST_PER_ENGINEER_RUN).")}


def render(report: dict[str, Any]) -> str:
    lines = [f"{report['users']} users, last {report['days']} days. {report['note']}",
             f"Typical user: ${report['profiles']['p50']['baseCostUsd']:.2f} + {report['profiles']['p50']['engineerRuns']:g} runs. "
             f"Heavy (p90): ${report['profiles']['p90']['baseCostUsd']:.2f} + {report['profiles']['p90']['engineerRuns']:g} runs.",
             "", f"{'plan':<18}{'price':>8}{'cap':>6}{'p50 margin':>12}{'p90 margin':>12}{'at cap':>9}  {'cap for ' + str(int(report['targetMargin'] * 100)) + '%'}"]
    for p in report["plans"]:
        def m(v: Any) -> str:
            return "—" if v is None else f"{v:.0%}"
        lines.append(f"{p['name']:<18}{p['priceUsd']:>8.0f}{'∞' if p['engineerRunCap'] is None else p['engineerRunCap']:>6}"
                     f"{m(p['p50']['margin']):>12}{m(p['p90']['margin']):>12}{m((p.get('atCap') or {}).get('margin')):>9}"
                     f"  {'—' if p.get('suggestedRunCap') is None else p['suggestedRunCap']}")
    return "\n".join(lines)


def main() -> None:  # pragma: no cover - CLI wrapper
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--days", type=int, default=30)
    args = parser.parse_args()
    report = analyze(get_store(), args.days)
    print(json.dumps(report, indent=2) if args.json else render(report))


if __name__ == "__main__":  # pragma: no cover
    main()
