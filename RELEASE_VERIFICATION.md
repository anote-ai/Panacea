# Panacea Release Verification

Every deployed frontend and backend build exposes public, non-secret metadata so
the running release can be matched to a Git commit:

- Frontend: `GET /build.json`
- Backend: `GET /health` and `GET /api/version`

The deployment workflow injects the GitHub commit SHA into both images. The
frontend uses `VITE_BUILD_SHA`; the backend Docker image uses
`PANACEA_BUILD_SHA`.

## Run the production smoke test

The checker only sends `GET` requests. It does not create users, upload files,
start payment sessions, or mutate production data.

```bash
python scripts/release_smoke.py \
  --frontend-url https://chat.anote.ai \
  --api-url https://chat.anote.ai \
  --expected-sha "$EXPECTED_SHA" \
  --require-payments
```

It verifies:

- the public frontend loads and identifies Panacea;
- frontend and backend build metadata match the expected commit;
- the API health endpoint is healthy;
- protected auth, document, and usage endpoints reject anonymous requests;
- the billing plans endpoint returns its expected JSON shape;
- at least one Stripe-backed paid plan is available when
  `--require-payments` is set.

Use the **Production Smoke Test** GitHub Actions workflow to run the same checks
manually after a deployment. A failure should block release sign-off until the
reported endpoint or build mismatch is resolved.

## Local tests

```bash
python -m unittest discover -s scripts/tests -v
```

The smoke checker uses only the Python standard library and performs normal TLS
certificate and hostname verification.
