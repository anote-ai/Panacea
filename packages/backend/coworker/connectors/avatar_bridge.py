"""Animated meeting avatar bridge.

The bridge owns the real-time lip-sync/video transport (for example Tavus
audio passthrough + Recall Output Media). Ourogen remains the only dialogue
and TTS engine and sends the already-generated ElevenLabs audio here.
"""
from __future__ import annotations

import os
from typing import Any

import requests

from coworker.connectors.base import ConnectorError

TIMEOUT = 30


def is_configured() -> bool:
    return bool(os.environ.get("MEETING_AVATAR_BRIDGE_URL") and os.environ.get("MEETING_AVATAR_BRIDGE_SECRET"))


def _base() -> str:
    return os.environ.get("MEETING_AVATAR_BRIDGE_URL", "").rstrip("/")


def _headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {os.environ.get('MEETING_AVATAR_BRIDGE_SECRET', '')}",
        "Content-Type": "application/json",
    }


def _call(method: str, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
    try:
        response = requests.request(method, f"{_base()}{path}", headers=_headers(), json=body, timeout=TIMEOUT)
    except requests.RequestException as exc:
        raise ConnectorError(f"Avatar bridge {path} could not be reached: {exc}") from exc
    if response.status_code >= 400:
        raise ConnectorError(f"Avatar bridge {path} failed ({response.status_code}): {response.text[:200]}")
    return response.json() if response.content else {}


def create_session(*, meeting_id: int, user_id: int, display_name: str,
                   greeting_text: str, greeting_mp3_b64: str | None) -> dict[str, str]:
    if not is_configured():
        raise ConnectorError("Animated meeting avatars are not configured.")
    data = _call("POST", "/sessions", {
        "meeting_id": meeting_id,
        "user_id": user_id,
        "display_name": display_name,
        "replica_id": os.environ.get("TAVUS_REPLICA_ID", ""),
        "greeting": {"text": greeting_text, "mp3_b64": greeting_mp3_b64},
    })
    session_id, camera_url = str(data.get("id") or ""), str(data.get("camera_url") or "")
    if not session_id or not camera_url.startswith("https://"):
        raise ConnectorError("Avatar bridge returned an invalid session or camera URL.")
    return {"id": session_id, "camera_url": camera_url}


def speak(session_id: str, mp3_b64: str, text: str = "") -> None:
    _call("POST", f"/sessions/{session_id}/speak", {"mp3_b64": mp3_b64, "text": text})


def stop(session_id: str) -> None:
    _call("POST", f"/sessions/{session_id}/stop")


def close(session_id: str) -> None:
    _call("DELETE", f"/sessions/{session_id}")
