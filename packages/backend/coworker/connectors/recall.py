"""Meeting bot via Recall.ai: join Zoom / Google Meet / Teams.

The bot joins with the name "<Name>'s AI coworker (Ourogen)", posts an AI
and recording disclosure in the meeting chat, streams transcripts to our
webhook, and can speak replies (TTS audio) or post them in chat.

Request shapes follow Recall's v1 bot API. Verify them against Recall's
current docs before relying on this outside the pilot.
"""
from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import ipaddress
import os
import time
from collections.abc import Mapping
from typing import Any
from urllib.parse import urlparse

import requests
from werkzeug.datastructures import Headers

from coworker.connectors.base import ConnectorError

TIMEOUT = 30

# Recall only accepts output_audio for bots created with automatic_audio_output,
# which needs a clip of its own. A 0.3s silent mp3 enables speaking without
# playing anything on join.
SILENT_MP3_B64 = (
    "SUQzBAAAAAAAI1RTU0UAAAAPAAADTGF2ZjYwLjE2LjEwMAAAAAAAAAAAAAAA//MYxAAAAANIAAAAAExBTUUzLjEwMFVVVVVVVVVVVVVVVVVV//MYxBcAAANIAAAAAFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV//MYxC4AAANIAAAAAFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV//MYxEUAAANIAAAAAFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV//MYxFwAAANIAAAAAFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV//MYxHMAAANIAAAAAFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV//MYxIoAAANIAAAAAFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV//MYxKEAAANIAAAAAFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV//MYxLgAAANIAAAAAFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV//MYxM8AAANIAAAAAFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV//MYxOYAAANIAAAAAFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV"
)


def is_configured() -> bool:
    return bool(os.environ.get("RECALL_API_KEY"))


def _verification_key() -> bytes | None:
    secret = os.environ.get("RECALL_WORKSPACE_VERIFICATION_SECRET", "")
    if not secret.startswith("whsec_"):
        return None
    try:
        key = base64.b64decode(secret.removeprefix("whsec_"), validate=True)
    except (binascii.Error, ValueError):
        return None
    return key or None


def bot_setup_issue() -> str:
    """Why a bot cannot safely join and receive live transcripts."""
    if not is_configured():
        return "Set RECALL_API_KEY on the server to join meetings."
    if not _verification_key():
        return "Set RECALL_WORKSPACE_VERIFICATION_SECRET from the Recall workspace to verify live transcripts."
    base = os.environ.get("BACKEND_URL", "").rstrip("/")
    url = urlparse(base)
    if url.scheme != "https" or not url.hostname or url.username or url.password or url.path or url.query or url.fragment:
        return "Set BACKEND_URL to the public HTTPS backend address so Recall can deliver transcripts."
    try:
        if ipaddress.ip_address(url.hostname).is_loopback or ipaddress.ip_address(url.hostname).is_private:
            return "Set BACKEND_URL to the public HTTPS backend address so Recall can deliver transcripts."
    except ValueError:
        if url.hostname == "localhost":
            return "Set BACKEND_URL to the public HTTPS backend address so Recall can deliver transcripts."
    return ""


def bot_ready() -> bool:
    return not bot_setup_issue()


def webhook_base_url() -> str:
    issue = bot_setup_issue()
    if issue:
        raise ConnectorError(issue)
    return os.environ["BACKEND_URL"].rstrip("/")


def verify_webhook(raw_body: bytes, headers: Mapping[str, str] | Headers) -> bool:
    """Verify Recall's workspace signature on the exact request bytes before parsing JSON."""
    key = _verification_key()
    message_id = headers.get("Webhook-Id")
    timestamp = headers.get("Webhook-Timestamp")
    signatures = headers.get("Webhook-Signature", "")
    if not key or not message_id or not timestamp or not signatures:
        return False
    try:
        if abs(time.time() - int(timestamp)) > 300:
            return False
    except ValueError:
        return False
    signed = message_id.encode() + b"." + timestamp.encode() + b"." + raw_body
    expected = hmac.new(key, signed, hashlib.sha256).digest()
    for versioned in signatures.split():
        version, _, signature = versioned.partition(",")
        if version != "v1" or not signature:
            continue
        try:
            provided = base64.b64decode(signature, validate=True)
        except (binascii.Error, ValueError):
            continue
        if hmac.compare_digest(expected, provided):
            return True
    return False


def _base() -> str:
    return os.environ.get("RECALL_API_BASE", "https://us-east-1.recall.ai/api/v1").rstrip("/")


def _headers() -> dict[str, str]:
    return {"Authorization": f"Token {os.environ.get('RECALL_API_KEY', '')}", "Content-Type": "application/json"}


def _call(method: str, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
    resp = requests.request(method, f"{_base()}{path}", headers=_headers(), json=body, timeout=TIMEOUT)
    if resp.status_code >= 400:
        raise ConnectorError(f"Recall {path} failed ({resp.status_code}): {resp.text[:200]}")
    data: dict[str, Any] = resp.json() if resp.content else {}
    return data


def transcript_provider() -> dict[str, Any]:
    """Recall's own streaming transcription in low-latency mode works on every platform with
    no host settings; ``RECALL_TRANSCRIPT=captions`` uses the platform's captions instead."""
    if os.environ.get("RECALL_TRANSCRIPT", "low_latency") == "captions":
        return {"meeting_captions": {}}
    return {"recallai_streaming": {"mode": "prioritize_low_latency", "language_code": "en"}}


def create_bot(meeting_url: str, bot_name: str, disclosure: str, webhook_url: str, *,
               greeting_mp3_b64: str | None = None, avatar_jpeg_b64: str | None = None) -> str:
    body = {
        "meeting_url": meeting_url,
        "bot_name": bot_name[:100],
        "chat": {"on_bot_join": {"send_to": "everyone", "message": disclosure[:500]}},
        "automatic_audio_output": {"in_call_recording": {"data": {"kind": "mp3", "b64_data": greeting_mp3_b64 or SILENT_MP3_B64}}},
        "recording_config": {
            "transcript": {"provider": transcript_provider()},
            "realtime_endpoints": [{"type": "webhook", "url": webhook_url, "events": ["transcript.data"]}],
        },
    }
    if avatar_jpeg_b64:
        body["automatic_video_output"] = {"in_call_recording": {"kind": "jpeg", "b64_data": avatar_jpeg_b64}}
    return str(_call("POST", "/bot/", body).get("id", ""))


def leave(bot_id: str) -> None:
    _call("POST", f"/bot/{bot_id}/leave_call/")


def stop_audio(bot_id: str) -> None:
    """Stop whatever the bot is saying (barge-in)."""
    _call("DELETE", f"/bot/{bot_id}/output_audio/")


def send_chat(bot_id: str, message: str) -> None:
    _call("POST", f"/bot/{bot_id}/send_chat_message/", {"message": message[:4000]})


def speak(bot_id: str, mp3_b64: str) -> None:
    _call("POST", f"/bot/{bot_id}/output_audio/", {"kind": "mp3", "b64_data": mp3_b64})


def parse_transcript_event(payload: dict[str, Any]) -> tuple[str, str, bool] | None:
    """Return (speaker_name, text, is_bot) from a transcript.data webhook."""
    data = (payload.get("data") or {}).get("data") or {}
    words = data.get("words") or []
    text = " ".join(w.get("text", "") for w in words).strip()
    if not text:
        return None
    participant = data.get("participant") or {}
    name = str(participant.get("name") or "Participant")
    return name, text, "ourogen" in name.lower()
