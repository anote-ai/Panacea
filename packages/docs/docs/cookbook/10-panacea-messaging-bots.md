# Panacea Multi-Channel Messaging Bots

This recipe explains Panacea's chat-ops style integrations: standalone Slack, SMS, and WhatsApp bots that let users ask coding questions from the messaging apps they already use.

## What you'll learn

- The shared design pattern across all three bots: receive → call an LLM → trim to the channel's character limit → reply
- How the Slack bot handles threading and edits a "thinking…" placeholder in place
- How the SMS/WhatsApp bots reply synchronously using Twilio's TwiML
- A current architectural gap worth knowing about before extending these bots

## Why this matters

Not every user wants to open a web UI or IDE to ask a question — chat-ops style integrations meet people where they already are. Each bot is a small, independently deployable Flask service, so a team can run just the channels they need (e.g. Slack only) without standing up the rest of Panacea's stack.

## Key Panacea files

| File | Why it matters |
|---|---|
| `Panacea/packages/bots/slack/app.py` | Slack Bolt app; supports Socket Mode or HTTP webhook; threaded "thinking…" placeholder updated in place |
| `Panacea/packages/bots/sms/app.py` | Twilio SMS webhook handler (`MessagingResponse`/TwiML) |
| `Panacea/packages/bots/whatsapp/app.py` | Twilio WhatsApp sandbox webhook handler |
| `Panacea/packages/bots/{slack,sms,whatsapp}/.env.example` | Required credentials per channel |

## How it works

1. **Slack** (`slack/app.py`): listens for `app_mention` events. `extract_query()` strips the `<@BOT_ID>` mention out of the message text. It immediately posts a `_Anote is thinking…_` placeholder message, then runs the LLM call on a background thread and either edits that placeholder in place via `client.chat_update(...)` or, if the placeholder post failed, sends a fresh threaded reply.
2. **SMS** (`sms/app.py`): Twilio POSTs each inbound text to `/sms` as form data (`Body`, `From`). The handler calls the LLM synchronously and returns a `MessagingResponse` (TwiML) with the reply — Twilio delivers it as a follow-up text.
3. **WhatsApp** (`whatsapp/app.py`): same TwiML pattern as SMS, wired to Twilio's WhatsApp sandbox webhook instead of a phone number.
4. All three call the **Anthropic API directly** (`anthropic.Anthropic(...).messages.create(...)`) with a shared system prompt describing Anote as a coding assistant — they do not currently proxy through Panacea's own backend, so they don't get RAG/document grounding, credit metering, or multi-agent orchestration from recipes 03/04/08.
5. Responses are trimmed to each channel's limit before sending: Slack 2900 characters, SMS/WhatsApp 1600 characters, each with a truncation notice appended if cut.

### Architectural gap to know about

Because these bots call Anthropic directly instead of routing through Panacea's backend, a Slack/SMS/WhatsApp user can't currently ask questions grounded in documents they've uploaded to Panacea, and their usage isn't metered through the credit system in recipe 08. If you want channel parity with the web UI, the natural next step is swapping the direct `anthropic_client.messages.create(...)` call for a request to Panacea's own `/v1/chat/completions` (recipe 07's OpenAI-compatible gateway) so these bots inherit RAG, orchestration, and billing for free.

## Run it locally

Each bot is independent — install and run only the ones you need.

### Slack

```bash
cd Panacea/packages/bots/slack
pip install -r requirements.txt
cp .env.example .env   # fill in SLACK_BOT_TOKEN, SLACK_SIGNING_SECRET, ANTHROPIC_API_KEY
python app.py
```

Set `SLACK_APP_TOKEN` in `.env` to run in Socket Mode (no public URL needed); otherwise it serves HTTP on `PORT` (default 3000) and expects Slack's Events API webhook pointed at `POST /slack/events`.

### SMS

```bash
cd Panacea/packages/bots/sms
pip install -r requirements.txt
cp .env.example .env   # fill in ANTHROPIC_API_KEY
python app.py
```

Configure your Twilio phone number's SMS webhook to `POST https://<your-host>/sms` (default port 3001).

### WhatsApp

```bash
cd Panacea/packages/bots/whatsapp
pip install -r requirements.txt
cp .env.example .env   # fill in ANTHROPIC_API_KEY
python app.py
```

Configure your Twilio WhatsApp sandbox webhook to point at `POST /whatsapp` on this service.

Each bot also exposes `GET /health` for a quick liveness check.

## Notes for the cookbook

This is a good "extend Panacea" recipe: readers can see the direct-to-Anthropic version working in minutes, then follow the architectural-gap note above to wire it through Panacea's backend instead for grounded, metered answers.
