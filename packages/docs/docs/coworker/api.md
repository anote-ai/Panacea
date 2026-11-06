# Coworker API

All routes live under `/api/coworker` and need a JWT (`Authorization: Bearer <token>`), except the OAuth callbacks, the meeting-bot webhook, pilot applications, and the public marketplace.

## API tokens

For the [SDK](../sdk/typescript.md#your-ai-coworker), the CLI (`anote coworker`) and scripts, create a personal access token in **Coworker → Settings → API tokens** (or `POST /tokens` with a signed-in session). Tokens start with `ogn_`, are shown once, and are stored only as a hash. Send one as `Authorization: Bearer ogn_…`.

A token works only on these routes: `GET`/`POST /engineer/runs`, `GET /engineer/runs/<id>`, `PATCH /engineer/runs/<id>/spec|graph`, `POST /engineer/runs/<id>/plan|start`, `GET`/`POST /reviews`, `GET /reviews/<id>`, `GET /scorecard`, `GET /knowledge-pack`, `GET /actions`, `GET /trial`. Anything else returns `403` with code `token_not_allowed`. **Approving, sending, billing, connections and token management need a signed-in session**, so a leaked token can't push code or spend money. `GET /tokens` lists your tokens; `DELETE /tokens/<id>` revokes one.

| Area | Routes |
|---|---|
| Setup | `GET /`, `POST /` (`{"mode": "demo" \| "live"}`), `PATCH /`, `POST /demo/simulate`, `POST /demo/reset` |
| Connections | `GET /connections`, `POST /connections/google/start`, `GET /connections/google/callback`, `POST /connections/microsoft/start`, `GET /connections/microsoft/callback`, `POST /connections/slack/start`, `GET /connections/slack/callback`, `POST /connections/slack/token`, `POST /slack/events` (Slack Events API, signed), `POST /connections/hubspot/start`, `GET /connections/hubspot/callback`, `POST /connections/hubspot/token`, `DELETE /connections/<provider>`, `POST /sync` (queues a background sync, returns `202`), `GET /sync/status` |
| Memory | `POST /memory/rebuild`, `GET /memory/learned`, `GET /memory/people`, `PATCH`/`DELETE /memory/people/<id>`, `GET /memory/timeline`, `DELETE /memory/<id>`, `GET /memory/recall?q=`, `GET /memory/status?name=`, `GET /inbox`, `GET /items/<id>` |
| Style | `GET /style`, `POST /style/rules`, `DELETE /style/rules` |
| Chat | `POST /chat/stream` (SSE events: `session_id`, `text`, `tool`, `card`, `title`, `error`, `done`) |
| Approvals | `GET /actions?status=&ids=`, `PATCH /actions/<id>`, `POST /actions/<id>/approve`, `/reject`, `/undo` |
| Oversight | `GET /activity` (`?format=csv`), `GET /digest`, `GET /status`, `POST /pause`, `POST /resume`, `POST /tick` |
| Responsibilities | `GET /responsibilities`, `POST /responsibilities`, `PATCH`/`DELETE /responsibilities/<id>`, `POST /responsibilities/<id>/run`, `GET /onboarding/suggestions` |
| Autonomy | `GET /autonomy`, `PUT /autonomy` |
| Calls | `GET`/`PUT /playbook`, `GET /meetings`, `POST /meetings`, `GET /meetings/<id>`, `POST /meetings/<id>/turn`, `POST /meetings/<id>/end`, `POST /meetings/recall/webhook` |
| Twin | `GET /twin`, `POST /twin/assets`, `GET /twin/assets/<id>/file`, `DELETE /twin/assets/<id>`, `POST /twin/consent/challenge`, `POST /twin/consent`, `POST /twin/voice`, `DELETE /twin`, `POST /twin/avatar/session`, `POST /voice/tts` |
| Billing & data | `GET /billing`, `POST /billing/checkout`, `GET /export`, `DELETE /data` |
| Pilot | `POST /pilot/applications` (public), `GET /pilot/applications` (`PILOT_ADMIN_EMAILS` only) |
| Developer tools | `POST /connections/github/start`, `POST /connections/github/token`, `POST /connections/notion/start`, `POST /connections/notion/token`, `POST /connections/jira/token`, `POST /connections/mcp`, `GET /mcp/<server>/tools`, `POST /mcp/<server>/call` ([guide](engineering/dev-tools.md)) |
| Knowledge pack | `GET /knowledge-pack`, `POST /knowledge-pack/build`, `PATCH /knowledge-pack`, `GET`/`POST /knowledge-pack/versions` ([guide](engineering/knowledge-packs.md)) |
| AI engineer | `GET`/`POST /engineer/runs`, `GET /engineer/runs/<id>`, `PATCH /engineer/runs/<id>/spec`, `POST /engineer/runs/<id>/plan`, `PATCH /engineer/runs/<id>/graph`, `POST /engineer/runs/<id>/start` ([guide](engineering/index.md)) |
| Scorecard | `GET /scorecard?days=&format=csv`, `GET /team/scorecard` (admins) ([guide](guide/scorecard.md)) |
| Trial | `GET`/`POST /trial`, `PUT /trial/goals`, `POST /trial/decide`; operators: `GET /operator/trials`, `GET /operator/trials/<id>`, `POST /operator/trials/<id>/notes` ([guide](guide/trial.md)) |
| Marketplace | Public: `GET /marketplace`, `GET /marketplace/ai/<slug>`; `GET /marketplace/me`, `POST /marketplace/publish`, `/unpublish`, `/payouts`, `POST /marketplace/ai/<slug>/hire`, `/rate`, `/report`, `POST /marketplace/hires/<id>/end` ([guide](engineering/marketplace.md)) |
| API tokens | `GET`/`POST /tokens`, `DELETE /tokens/<id>` (signed-in session only) |
| Code review | `GET`/`POST /reviews`, `GET /reviews/<id>`, `POST /reviews/<id>/findings/<finding>/dismiss` ([guide](engineering/code-review.md)) |

## Example: delegate in chat

```bash
curl -N -X POST http://localhost:5000/api/coworker/chat/stream \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"message": "Reply to Dana"}'
```

The stream includes a `card` event with the proposed email. Approve it:

```bash
curl -X POST http://localhost:5000/api/coworker/actions/12/approve -H "Authorization: Bearer $TOKEN"
```

## Example: a scheduled task

Create a recurring job. `freq` is `daily`, `weekdays`, `weekly` (with `days`), `monthly` (with `day`), or `hourly` (with `every_hours`). Times are in the owner's time zone.

```bash
curl -X POST http://localhost:5000/api/coworker/responsibilities \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"instruction": "Summarize my open deals and who I should follow up with",
       "schedule": {"freq": "weekly", "days": ["mon"], "time": "09:00", "deliver": ["email"]}}'
```

The response includes `schedule.description` ("Every Monday at 9 AM"), `schedule.nextRun`, and the last runs. `PATCH /responsibilities/<id>` with `{"schedule": {...}}` changes it. `POST /responsibilities/<id>/run` runs it now. In chat, "every Monday at 9 summarize my open deals" proposes the same task.

Each occurrence runs once, even with several workers. A run missed by up to 2 hours (for example during a deploy) still runs; older ones are skipped. A run uses the same tools as chat, and anything it sends follows the task's autonomy level and your organization's limits.



`POST /sync` returns in well under a second. The sync runs in the background:

```bash
curl -X POST "http://localhost:5000/api/coworker/sync?rebuild=1" -H "Authorization: Bearer $TOKEN"
curl http://localhost:5000/api/coworker/sync/status -H "Authorization: Bearer $TOKEN"
# {"running": true, "total": 412, "items": {"gmail": 380, "gcal": 32}, "job": {"phase": "syncing", ...}}
```

Phases go `queued`, `syncing`, `learning`, then `done` or `error`.

## Example: hand off a ticket to the AI engineer

```bash
# 1. Draft a spec from a Jira ticket (or send {"text": "..."} from chat)
curl -X POST $API/api/coworker/engineer/runs -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' -d '{"source": "jira:ACME-142"}'
# {"id": 7, "status": "spec", "spec": {"goal": "Annual billing: ...", "acceptance_criteria": [...]}, ...}

# 2. Confirm it and build the task graph
curl -X POST $API/api/coworker/engineer/runs/7/plan -H "Authorization: Bearer $TOKEN"
# {"status": "planned", "layers": [["impl"], ["docs", "test"]], ...}

# 3. Run it: code, tests, review, slop checks, then a github.pr action to approve
curl -X POST $API/api/coworker/engineer/runs/7/start -H "Authorization: Bearer $TOKEN"
# {"status": "ready", "checks": {"passed": true}, "slop": {"score": 100}, "actionId": 42, ...}

# 4. Approve the pull request
curl -X POST $API/api/coworker/actions/42/approve -H "Authorization: Bearer $TOKEN"
```
