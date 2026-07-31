"""
Anote Slack Bot
===============
Listens for @anote mentions in Slack channels and replies with AI responses
from the Anote backend.

Usage:
    pip install -r requirements.txt
    cp .env.example .env   # fill in your credentials
    python app.py
"""

import logging
import os
import re
import threading
from typing import Optional

import requests
from anthropic import Anthropic
from dotenv import load_dotenv
from flask import Flask, request
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("anote.slack")

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN", "")
MODEL = os.environ.get("ANOTE_MODEL", "claude-sonnet-4-6")
MAX_TOKENS = int(os.environ.get("ANOTE_MAX_TOKENS", "4096"))
PORT = int(os.environ.get("PORT", "3000"))
SLACK_MAX_CHARS = 2900
ANOTE_BACKEND_URL = os.environ.get("ANOTE_BACKEND_URL", "http://localhost:5000")

ANOTE_SYSTEM_PROMPT = """\
You are Anote, an expert AI coding assistant built by Anote AI.
You help developers write better code, fix bugs, explain concepts, review code,
generate tests, and refactor. You are responding via Slack — keep replies clear
and concise. Use Slack mrkdwn formatting (backticks for inline code, triple
backticks for code blocks). Avoid excessive markdown headers.
"""

anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)


def call_anote_backend(prompt: str) -> str:
    logger.info("Calling Anote backend with prompt: %r", prompt[:120])
    try:
        response = anthropic_client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=ANOTE_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        text = response.content[0].text if response.content else ""
        logger.info("Anote backend returned %d chars", len(text))
        return text
    except Exception as exc:
        logger.error("Anthropic API error: %s", exc, exc_info=True)
        raise


def trim_response(text: str, max_chars: int = SLACK_MAX_CHARS) -> str:
    if len(text) <= max_chars:
        return text
    cutoff = max_chars - 100
    return text[:cutoff] + "\n\n_(Response truncated — ask me to continue.)_"


def extract_query(text: str) -> Optional[str]:
    cleaned = re.sub(r"<@[A-Z0-9]+>", "", text, flags=re.IGNORECASE).strip()
    return cleaned if cleaned else None


slack_app = App(
    token=SLACK_BOT_TOKEN,
    signing_secret=SLACK_SIGNING_SECRET,
)


def build_blocks(text: str) -> list:
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": trim_response(text),
            },
        }
    ]


@slack_app.event("app_mention")
def handle_mention(event, say, client, logger):
    text: str = event.get("text", "")
    channel: str = event["channel"]
    thread_ts: str = event.get("thread_ts", event["ts"])
    event_ts: str = event["ts"]

    logger.info(
        "app_mention — user=%s channel=%s text=%r",
        event.get("user"),
        channel,
        text[:80],
    )

    query = extract_query(text)
    if not query:
        say(
            text="Hi! Mention me with a question or command, e.g. `@anote explain src/index.ts`",
            thread_ts=thread_ts,
        )
        return

    thinking_ts: Optional[str] = None
    try:
        result = say(text="_Anote is thinking…_", thread_ts=event_ts)
        thinking_ts = result.get("ts") if result else None
    except Exception as exc:
        logger.warning("Could not post thinking message: %s", exc)

    def _run():
        try:
            answer = call_anote_backend(query)
        except Exception as exc:
            answer = f":warning: Anote encountered an error:\n```\n{exc}\n```"

        blocks = build_blocks(answer)

        try:
            if thinking_ts:
                client.chat_update(
                    channel=channel,
                    ts=thinking_ts,
                    text=answer,
                    blocks=blocks,
                )
            else:
                say(text=answer, blocks=blocks, thread_ts=event_ts)
        except Exception as exc:
            logger.error("Failed to post Slack reply: %s", exc, exc_info=True)

    threading.Thread(target=_run, daemon=True).start()


@slack_app.event("message")
def handle_message_events(event, logger):
    subtype = event.get("subtype", "")
    if subtype in ("bot_message", "message_changed", "message_deleted"):
        return
    logger.debug("Unhandled message event subtype=%r", subtype)


# ── Remote approvals: resolve a paused CLI session from Slack ──────────────
# The counterpart to packages/cli/src/remoteApproval.ts — a CLI session pauses on
# a risky tool call and posts it to the backend; this surfaces it here so it can
# be resolved without anyone being at the terminal.


def fetch_pending_approvals() -> list:
    resp = requests.get(f"{ANOTE_BACKEND_URL}/api/approvals", params={"status": "pending"}, timeout=5)
    resp.raise_for_status()
    return resp.json().get("approvals", [])


def resolve_approval(approval_id: str, approved: bool, responder: str) -> dict:
    resp = requests.post(
        f"{ANOTE_BACKEND_URL}/api/approvals/{approval_id}/respond",
        json={"approved": approved, "responder": responder},
        timeout=5,
    )
    resp.raise_for_status()
    return resp.json()


def build_approval_blocks(approval: dict) -> list:
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f"*Session* `{approval['session_id']}` wants to run "
                    f"*{approval['action']}*\n```{approval.get('detail', '')[:500]}```"
                ),
            },
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Approve"},
                    "style": "primary",
                    "action_id": "approval_approve",
                    "value": approval["id"],
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Deny"},
                    "style": "danger",
                    "action_id": "approval_deny",
                    "value": approval["id"],
                },
            ],
        },
    ]


@slack_app.command("/anote-approvals")
def handle_approvals_command(ack, respond, logger):
    ack()
    try:
        approvals = fetch_pending_approvals()
    except Exception as exc:
        logger.error("Failed to fetch approvals: %s", exc, exc_info=True)
        respond(text=f":warning: Could not reach the approvals backend: {exc}")
        return

    if not approvals:
        respond(text="No pending approvals. :white_check_mark:")
        return

    for approval in approvals:
        respond(blocks=build_approval_blocks(approval), text=f"Approval needed: {approval['action']}")


def _handle_approval_action(ack, body, client, logger, approved: bool):
    ack()
    approval_id = body["actions"][0]["value"]
    responder = f"slack:{body['user']['username']}"
    try:
        approval = resolve_approval(approval_id, approved, responder)
    except Exception as exc:
        logger.error("Failed to resolve approval %s: %s", approval_id, exc, exc_info=True)
        client.chat_postMessage(
            channel=body["channel"]["id"],
            text=f":warning: Could not resolve approval `{approval_id}`: {exc}",
        )
        return

    verb = "approved" if approved else "denied"
    client.chat_update(
        channel=body["channel"]["id"],
        ts=body["message"]["ts"],
        text=f"Approval {verb} by @{body['user']['username']}",
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{approval['action']}* was *{verb}* by <@{body['user']['id']}>",
                },
            }
        ],
    )


@slack_app.action("approval_approve")
def handle_approval_approve(ack, body, client, logger):
    _handle_approval_action(ack, body, client, logger, approved=True)


@slack_app.action("approval_deny")
def handle_approval_deny(ack, body, client, logger):
    _handle_approval_action(ack, body, client, logger, approved=False)


flask_app = Flask(__name__)
handler = SlackRequestHandler(slack_app)


@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)


@flask_app.route("/health", methods=["GET"])
def health():
    return {"status": "ok", "service": "anote-slack-bot"}


if __name__ == "__main__":
    if SLACK_APP_TOKEN:
        from slack_bolt.adapter.socket_mode import SocketModeHandler
        logger.info("Starting Slack bot in Socket Mode…")
        socket_handler = SocketModeHandler(slack_app, SLACK_APP_TOKEN)
        socket_handler.start()
    else:
        logger.info("Starting Slack bot in HTTP mode on port %d…", PORT)
        flask_app.run(host="0.0.0.0", port=PORT)
