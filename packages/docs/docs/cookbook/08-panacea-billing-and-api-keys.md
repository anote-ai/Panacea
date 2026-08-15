# Panacea Billing, API Keys & Credit Metering

This recipe explains how Panacea meters usage, authenticates API callers, and turns Stripe subscriptions into a spendable credit balance.

## What you'll learn

- The three ways a request can authenticate: JWT, session token, or long-lived API key
- How credits are checked and deducted per request, and how usage is logged
- How a Stripe subscription checkout flows through to a refreshed credit balance
- How users generate, list, and revoke their own API keys
- The abuse guardrails that gate new/changed subscriptions

## Why this matters

Panacea isn't just a RAG demo — it's a metered product with real subscription tiers. Every document upload, chat completion, or evaluation call costs credits, and credits are replenished by an active Stripe subscription. This recipe walks through the full loop: how a caller proves who they are, how that identity is priced, and how money (via Stripe) turns back into usable credits.

## Key Panacea files

| File | Why it matters |
|---|---|
| `Panacea/backend/database/db_auth.py` | `extractUserEmailFromRequest()` tries JWT → session token → API key in sequence; `user_has_credits()`, `api_key_user_has_credits()`, `deduct_credits_from_api_key_user()`; abuse guardrails in `verifyAuthForNewSubscriptipns()` |
| `Panacea/backend/database/usage.py` | `log_api_usage()` writes one row per request to `api_usage`; `get_usage_summary()` / `get_usage_rows()` power usage reporting |
| `Panacea/backend/api_endpoints/payments/handler.py` | `CreateCheckoutSessionHandler`, `CreatePortalSessionHandler`, `StripeWebhookHandler` |
| `Panacea/backend/api_endpoints/generate_api_key/handler.py`, `get_api_keys/handler.py`, `delete_api_key/handler.py`, `refresh_credits/handler.py` | Mint, list, revoke API keys; manually refresh credits |
| `Panacea/backend/stripe_config/portal_config.py` | Per-tier Stripe Billing Portal configuration |

## How it works

1. **Authenticate.** Every protected route calls `extractUserEmailFromRequest(request)`, which reads the `Authorization: Bearer <token>` header and tries, in order: decode as a JWT, look up as a session token (`user_email_for_session_token`), then look up as an API key (`user_email_for_api_key`). Whichever succeeds first resolves the caller's email.
2. **Check credits.** Before serving a request, the backend calls `user_has_credits(user_email)` (JWT/session callers) or `api_key_user_has_credits(api_key)` (API-key callers) to confirm the user's `credits` column in `users` is at least 1.
3. **Deduct and log.** On completion, `deduct_credits_from_api_key_user()` decrements the balance and `log_api_usage()` inserts a row into `api_usage` with the endpoint, model, token counts, and credits spent — this is what powers `GET /v1/usage` and `GET /v1/account`.
4. **Upgrade via Stripe.** The frontend calls `POST /createCheckoutSession`, which hits `CreateCheckoutSessionHandler`: it resolves the user, maps the requested `product_hash` to a Stripe price ID, and creates a `stripe.checkout.Session` in `subscription` mode (optionally applying a 30-day free trial code).
5. **Webhook completes the loop.** Stripe calls back `POST /stripeWebhook` on `checkout.session.completed`; `StripeWebhookHandler` records the new subscription via `add_subscription()` and calls `refresh_credits(user_email)` to top up the user's balance. `customer.subscription.updated` (cancellation) and `.deleted` events are handled symmetrically.
6. **Manage the subscription.** `POST /createPortalSession` (`CreatePortalSessionHandler`) opens a Stripe Billing Portal session scoped to the user's current tier via `config_for_payment_tiers()`, so upgrades/downgrades/cancellations happen through Stripe's hosted UI.
7. **API keys.** `POST /generateAPIKey` requires at least 1 credit and calls `generate_api_key()`; `GET /getAPIKeys` and `POST /deleteAPIKey` list/revoke keys, each tracked with a `last_used` timestamp (`touch_api_key_last_used`).

### Abuse guardrails

`verifyAuthForNewSubscriptipns()` in `db_auth.py` caps new subscriptions per tier per day (e.g. 25/day for Premium, 5/day for Enterprise), emails an internal alert at defined thresholds (5, 10, 50, 100, 200, 500 new subscriptions/day), and blocks a user from changing plans more than once in a rolling month.

## Run it locally

From the workspace root (`anote/panacea`):

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

Set these in `backend/.env` to exercise the billing flow:

```bash
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
FRONTEND_URL=http://localhost:3000
JWT_SECRET_KEY=some-dev-secret
```

Forward Stripe webhooks to your local backend with the Stripe CLI:

```bash
stripe listen --forward-to localhost:5000/stripeWebhook
```

### Try it

```bash
# Generate an API key (requires an authenticated JWT/session, and >=1 credit)
curl -X POST http://localhost:5000/generateAPIKey \
  -H "Authorization: Bearer <jwt_or_session_token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "my first key"}'

# Check usage with the new API key
curl http://localhost:5000/v1/usage \
  -H "Authorization: Bearer <api_key>"
```

## Notes for the cookbook

Pair this with recipe 07 (OpenAI-Compatible API Gateway) — the same API keys generated here are what authenticate `AnoteOpenAI` calls. Worth flagging the `verifyAuthForNewSubscriptipns` typo in the function name as a known quirk if a reader goes looking for it in the code.
