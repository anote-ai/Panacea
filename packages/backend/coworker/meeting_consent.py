"""Consent gate for real meeting bots.

Recall does not receive the meeting URL and no bot is created until an
attendee opens the signed link and confirms that everyone joining agreed to
AI note-taking. The link is bearer access, expires after seven days, and can
only move one pending meeting to a final decision once.
"""
from __future__ import annotations

import logging
import os
from typing import Any

from itsdangerous import BadSignature, SignatureExpired, URLSafeSerializer, URLSafeTimedSerializer

from coworker import bot_media
from coworker.connectors import avatar_bridge, recall
from coworker.store import Store, iso

MAX_AGE_SECONDS = 7 * 24 * 60 * 60
log = logging.getLogger("coworker.meeting_consent")


class ConsentLinkError(ValueError):
    pass


def _serializer(secret: str) -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(secret, salt="meeting-consent")


def request(store: Store, user_id: int, meeting: dict[str, Any], *, secret: str, frontend_url: str,
            auto_start: bool = True) -> dict[str, Any]:
    token = _serializer(secret).dumps({"u": user_id, "m": meeting["id"]})
    consent_url = f"{frontend_url.rstrip('/')}/meeting-consent/{token}"
    answers = {**(meeting.get("answers") or {}), "consent_token": token, "consent_url": consent_url,
               "consent_auto_start": auto_start}
    metrics = {**(meeting.get("metrics") or {}), "consent": "link_pending", "consent_method": "link"}
    store.update("cw_meetings", meeting["id"], user_id, {
        "status": "awaiting_consent", "answers": answers, "metrics": metrics, "transcript": [],
    })
    result = store.get("cw_meetings", meeting["id"], user_id)
    assert result is not None
    return result


def resolve(store: Store, token: str, secret: str) -> dict[str, Any]:
    try:
        claims = _serializer(secret).loads(token, max_age=MAX_AGE_SECONDS)
        user_id, meeting_id = int(claims["u"]), int(claims["m"])
    except SignatureExpired as exc:
        raise ConsentLinkError("This consent link has expired. Ask the organizer for a new link.") from exc
    except (BadSignature, KeyError, TypeError, ValueError) as exc:
        raise ConsentLinkError("This consent link is invalid.") from exc
    meeting = store.get("cw_meetings", meeting_id, user_id)
    if not meeting or (meeting.get("answers") or {}).get("consent_token") != token:
        raise ConsentLinkError("This consent link is invalid.")
    return meeting


def decide(store: Store, token: str, secret: str, agree: bool) -> dict[str, Any]:
    meeting = resolve(store, token, secret)
    user_id, meeting_id = int(meeting["user_id"]), int(meeting["id"])
    if meeting["status"] in ("consent_granted", "starting", "active", "declined"):
        return meeting
    if meeting["status"] != "awaiting_consent":
        raise ConsentLinkError("This meeting is no longer waiting for consent.")
    if not agree:
        store.update("cw_meetings", meeting_id, user_id, {
            "status": "declined", "ended_at": iso(),
            "metrics": {**(meeting.get("metrics") or {}), "consent": "declined", "consent_decided_at": iso()},
        })
        result = store.get("cw_meetings", meeting_id, user_id)
        assert result is not None
        return result

    # Claim the transition before contacting vendors so repeated clicks cannot
    # create multiple bots for the same meeting.
    claimed = store.execute(
        "UPDATE cw_meetings SET status = %s WHERE id = %s AND user_id = %s AND status = %s",
        ("starting", meeting_id, user_id, "awaiting_consent"),
    )
    if not claimed:
        current = store.get("cw_meetings", meeting_id, user_id)
        if current:
            return current
        raise ConsentLinkError("This meeting is no longer available.")
    metrics = {**(meeting.get("metrics") or {}), "consent": "granted", "consent_decided_at": iso()}
    store.update("cw_meetings", meeting_id, user_id, {"metrics": metrics})
    if not (meeting.get("answers") or {}).get("consent_auto_start", True):
        store.update("cw_meetings", meeting_id, user_id, {"status": "consent_granted"})
        result = store.get("cw_meetings", meeting_id, user_id)
        assert result is not None
        return result
    try:
        return _start_bot(store, user_id, meeting_id, secret)
    except Exception:
        store.update("cw_meetings", meeting_id, user_id, {"status": "failed"})
        raise


def start_granted(store: Store, user_id: int, meeting_id: int, secret: str) -> dict[str, Any]:
    """Start a pre-consented scheduled bot when its meeting time arrives."""
    claimed = store.execute(
        "UPDATE cw_meetings SET status = %s WHERE id = %s AND user_id = %s AND status = %s",
        ("starting", meeting_id, user_id, "consent_granted"),
    )
    if not claimed:
        meeting = store.get("cw_meetings", meeting_id, user_id)
        if meeting and meeting.get("status") in ("starting", "active"):
            return meeting
        raise ConsentLinkError("Attendee consent has not been granted for this meeting.")
    try:
        return _start_bot(store, user_id, meeting_id, secret)
    except Exception:
        store.update("cw_meetings", meeting_id, user_id, {"status": "failed"})
        raise


def _start_bot(store: Store, user_id: int, meeting_id: int, secret: str) -> dict[str, Any]:
    meeting = store.get("cw_meetings", meeting_id, user_id)
    if not meeting:
        raise ConsentLinkError("Meeting not found.")
    coworker = store.get_coworker(user_id) or {}
    first = (coworker.get("owner_name") or "the team").split(" ")[0]
    greeting = (f"Hi, I'm {first}'s AI coworker. I'm an AI, not {first}. "
                "You approved the consent link before I joined. Before we begin, please confirm out loud that "
                "you're okay with me participating and taking notes. Is that okay?")
    audio = bot_media.greeting(store, user_id, greeting)
    avatar = bot_media.camera_frame(store, user_id)
    avatar_session: dict[str, str] | None = None
    if avatar_bridge.is_configured() and audio:
        try:
            avatar_session = avatar_bridge.create_session(
                meeting_id=meeting_id, user_id=user_id,
                display_name=f"{first}'s AI coworker (Ourogen)", greeting_text=greeting,
                greeting_mp3_b64=audio,
            )
        except Exception as exc:
            # Calls must remain usable if the optional avatar vendor is down.
            log.warning("animated avatar unavailable for meeting %s; using photo fallback: %s", meeting_id, exc)
            avatar_session = None
    webhook_token = URLSafeSerializer(secret, salt="recall-webhook").dumps({"u": user_id, "m": meeting_id})
    hook = f"{recall.webhook_base_url()}/api/coworker/meetings/recall/webhook?token={webhook_token}"
    try:
        bot_id = recall.create_bot(
            meeting["meeting_url"], f"{first}'s AI coworker (Ourogen)",
            f"I'm {first}'s disclosed AI coworker. Link consent was recorded before I joined, and I'm asking for "
            "spoken confirmation now. Say 'no' or 'please leave' and I will.", hook,
            greeting_mp3_b64=None if avatar_session else audio,
            avatar_jpeg_b64=None if avatar_session else avatar,
            avatar_page_url=avatar_session["camera_url"] if avatar_session else None,
        )
    except Exception:
        if avatar_session:
            try:
                avatar_bridge.close(avatar_session["id"])
            except Exception:
                pass
        raise
    transcript = [{"speaker": "coworker", "text": greeting, "at": iso(), "kind": "disclosure"}]
    metrics = {**(meeting.get("metrics") or {}), "spoken_confirmation": "pending",
               "spoken_confirmation_asked": 0,
               "audio_status": "avatar_queued" if avatar_session else ("greeting_queued" if audio else "chat_only")}
    if avatar_session:
        metrics["avatar_session_id"] = avatar_session["id"]
        metrics["avatar_mode"] = "animated"
    else:
        metrics["avatar_mode"] = "photo"
    store.update("cw_meetings", meeting_id, user_id, {
        "status": "active", "bot_id": bot_id, "transcript": transcript, "metrics": metrics,
    })
    store.log(user_id, "meeting", f"Consent received; bot is joining: {meeting['title']}", {"meeting_id": meeting_id})
    result = store.get("cw_meetings", meeting_id, user_id)
    assert result is not None
    return result


def frontend_url() -> str:
    return os.environ.get("FRONTEND_URL", "http://localhost:3000").rstrip("/")
