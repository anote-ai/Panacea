# Plans and pricing

Two plan lineups exist in the code. Existing subscribers keep their plan whichever lineup is offered.

| Lineup | Plans | Offered when |
|---|---|---|
| **Current** | Free, Coworker ($199), Coworker + Calls ($599), Team ($1,000) | default |
| **Hire an AI (v3)** | Free (starter), **Pro ($50/month)**, **Enterprise (per seat, default $1,650)** | `COWORKER_PRICING_V3=1` |

The v3 lineup is behind a flag on purpose: **turn it on only after checking the margins below against real usage.**

| v3 plan | Price | Includes | Engineer runs / month |
|---|---|---|---|
| Free | $0 | Email, calendar, memory | 3 |
| Pro | $50 | Email, Slack, calendar, memory, AI engineer | 12 |
| Enterprise | `COWORKER_ENTERPRISE_SEAT_USD` per seat (default $1,650, about a tenth of a $200k engineer) | Everything, including calls, twin, admin, SSO | Unlimited |

Enterprise is a seat plan like Team: every member of the paying organization gets it, and the Stripe subscription's quantity follows the organization's seats. Limits are enforced only with `COWORKER_ENFORCE_PLANS=1`. Over a limit, starting an engineer run returns `402` with code `plan_limit`.

## Check the margins first

```bash
cd packages/backend
COWORKER_DB_URL=<production> python -m coworker.pricing
```

For every user, it measures the last 30 days of variable cost: metered model spend (scheduled tasks and engineer runs), call minutes, text-to-speech, and executed actions. It then prices each plan for a typical user (p50) and a heavy user (p90), with the plan's caps applied. For each plan it shows:

- the margin at p50 and p90;
- the margin for a heavy user who uses **every** engineer run the cap allows;
- the largest engineer-run cap that keeps a heavy user at the target margin (`COWORKER_TARGET_MARGIN`, default 60%).

Operators can also read it at `GET /api/coworker/operator/pricing`.

Until there are metered engineer runs, it assumes $1.50 a run (`COWORKER_COST_PER_ENGINEER_RUN`). At that cost, Pro with 20 runs falls to a 40% margin for a heavy user, which is why Pro is capped at 12 for now. Re-run it after the pilot and adjust `ENGINEER_RUNS` in `coworker/billing.py`.

## Turning on v3

1. Run the analysis on production data and settle the caps.
2. Create the Stripe prices: Pro as a flat monthly price, and Enterprise as a **per-unit** monthly price. Set `STRIPE_PRICE_COWORKER_PRO` and `STRIPE_PRICE_COWORKER_ENTERPRISE`.
3. Set `COWORKER_PRICING_V3=1`, and `COWORKER_ENFORCE_PLANS=1` when the pilot ends.
4. Update the pricing section of the landing site.
