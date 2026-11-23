"""Turn-taking for live meeting-bot calls.

The meeting bot streams transcript segments to our webhook. Answering each
segment as it lands makes the coworker talk over people who pause mid-thought,
answer "mm-hm", and keep talking when interrupted. Instead:

* **Backchannels** ("mm-hm", "yeah", "right") never start a turn.
* **End of turn**: segments are buffered in ``cw_turns``; the coworker
  answers once the other side has been quiet for ``COWORKER_TURN_SILENCE``
  seconds, with everything they said in that turn. The buffer lives in the
  database, so it works across server processes; the claim is an atomic
  ``UPDATE``, so one turn gets one reply.
* **Barge-in**: if they start talking while the coworker is speaking, the
  bot's audio is stopped and their words become the next turn.
* **Latency masking**: if the reply takes longer than ``FILLER_AFTER``
  seconds, the coworker says a short "Good question." first.
* Replies use ``llm.call_model`` (a fast model) and are kept short.
* **First sentence first**: a longer reply starts playing as soon as its first
  sentence is synthesized, while the rest is still being generated.

Per-turn timings land in the meeting's metrics (``turn_ms``) so p50/p95 can
be measured on real calls.
"""
from __future__ import annotations

import base64
import logging
import os
import re
import threading
import time
from typing import Any

from coworker.store import Store, iso

log = logging.getLogger("coworker.live_call")

FILLER_AFTER = 1.2
WORDS_PER_SECOND = 2.6  # spoken pace, to know roughly when the bot stops talking
BACKCHANNEL_RE = re.compile(
    r"^(?:(?:mm+[- ]?hm+|uh[- ]?huh|hmm+|yeah|yep|yup|yes|right|okay|ok|sure|got it|i see|cool|great|nice|wow|"
    r"ah+|oh+|uh+|um+|alright|true|exactly|makes sense|totally)[\s,.!]*){1,3}$",
    re.IGNORECASE,
)
_audio_cache: dict[tuple[str, str], bytes] = {}
_cache_lock = threading.Lock()


def silence_seconds() -> float:
    try:
        return max(0.0, float(os.environ.get("COWORKER_TURN_SILENCE", "0.8")))
    except ValueError:
        return 0.8


def is_backchannel(text: str) -> bool:
    return bool(BACKCHANNEL_RE.match((text or "").strip()))


def _speaking_until(meeting: dict[str, Any]) -> float:
    return float((meeting.get("metrics") or {}).get("speaking_until") or 0)


def _set_metric(store: Store, user_id: int, meeting_id: int, **values: Any) -> None:
    meeting = store.get("cw_meetings", meeting_id, user_id) or {}
    store.update("cw_meetings", meeting_id, user_id, {"metrics": {**(meeting.get("metrics") or {}), **values}})


def on_segment(store: Store, user_id: int, meeting_id: int, text: str) -> int | None:
    """Record what the other side just said. Returns the turn row id, or None if ignored."""
    text = (text or "").strip()
    meeting = store.get("cw_meetings", meeting_id, user_id)
    if not text or not meeting or meeting["status"] != "active":
        return None
    # A bare "yes"/"okay" is the answer to an opening consent question,
    # not a backchannel. Once both consent gates are decided, suppress such small talk.
    metrics = meeting.get("metrics") or {}
    awaiting_confirmation = metrics.get("consent") == "pending" or metrics.get("spoken_confirmation") == "pending"
    if is_backchannel(text) and not awaiting_confirmation:
        return None
    if _speaking_until(meeting) > time.time() and meeting.get("bot_id"):
        from coworker.connectors import recall
        from coworker.connectors.base import ConnectorError

        try:
            recall.stop_audio(meeting["bot_id"])
        except ConnectorError as exc:
            log.info("couldn't stop bot audio: %s", exc)
        metrics = meeting.get("metrics") or {}
        _set_metric(store, user_id, meeting_id, speaking_until=0, barge_ins=int(metrics.get("barge_ins", 0)) + 1)
    return store.insert("cw_turns", {"user_id": user_id, "meeting_id": meeting_id, "text": text, "created_at": iso()})


def claim(store: Store, user_id: int, meeting_id: int, turn_id: int) -> str:
    """Take every waiting segment if ``turn_id`` is still the latest; '' if a newer one will answer."""
    latest = store.one("SELECT MAX(id) AS id FROM cw_turns WHERE meeting_id = %s AND user_id = %s AND status = 'new'",
                       (meeting_id, user_id))
    if not latest or int(latest.get("id") or 0) != turn_id:
        return ""
    taken = store.execute("UPDATE cw_turns SET status = 'taken', claimed_by = %s WHERE meeting_id = %s AND user_id = %s "
                          "AND status = 'new' AND id <= %s", (turn_id, meeting_id, user_id, turn_id))
    if not taken:
        return ""  # another process took it
    rows = store.query("SELECT text FROM cw_turns WHERE meeting_id = %s AND claimed_by = %s ORDER BY id", (meeting_id, turn_id))
    return " ".join(r["text"] for r in rows).strip()


def _audio(text: str, voice_id: str | None) -> bytes:
    from coworker import voice

    key = (voice_id or "", text)
    with _cache_lock:
        cached = _audio_cache.get(key)
    if cached is not None:
        return cached
    audio = voice.tts(text, voice_id)
    if len(text) < 40:  # fillers repeat; full replies don't
        with _cache_lock:
            _audio_cache[key] = audio
    return audio


MP3_BITS_PER_SECOND = 128_000  # ElevenLabs mp3_44100_128
SENTENCE_RE = re.compile(r"(.+?[.!?])\s+(.+)", re.S)


def mp3_seconds(audio: bytes) -> float:
    return len(audio) * 8 / MP3_BITS_PER_SECOND


def split_first_sentence(text: str) -> tuple[str, str]:
    """('First sentence.', 'the rest') when the reply has more than one sentence worth splitting."""
    m = SENTENCE_RE.match(text.strip())
    if not m or len(m.group(1).split()) < 3:
        return text.strip(), ""
    return m.group(1).strip(), m.group(2).strip()


def _say(store: Store, user_id: int, meeting: dict[str, Any], text: str) -> str:
    """Speak ``text``. Longer replies start after the first sentence's audio is ready,
    while the rest is still being synthesized, and stop if the other side interrupts."""
    from concurrent.futures import ThreadPoolExecutor

    from coworker import voice
    from coworker.connectors import recall

    if not meeting.get("bot_id") or not text:
        return "unavailable"
    if not voice.is_configured():
        recall.send_chat(meeting["bot_id"], text)
        return "chat_only"
    voice_id = ((store.get_coworker(user_id) or {}).get("settings") or {}).get("voice_id")
    first, rest = split_first_sentence(text)
    if not rest:
        audio = _audio(text, voice_id)
        recall.speak(meeting["bot_id"], base64.b64encode(audio).decode())
        _set_metric(store, user_id, meeting["id"], speaking_until=time.time() + mp3_seconds(audio))
        return "sent"
    with ThreadPoolExecutor(max_workers=1) as pool:
        later = pool.submit(_audio, rest, voice_id)
        head = _audio(first, voice_id)
        started = time.time()
        # Marked before the audio goes out (and long enough to cover the rest), so any interruption is caught.
        _set_metric(store, user_id, meeting["id"],
                    speaking_until=started + mp3_seconds(head) + len(rest.split()) / WORDS_PER_SECOND)
        recall.speak(meeting["bot_id"], base64.b64encode(head).decode())
        tail = later.result()
    wait = mp3_seconds(head) - (time.time() - started) - 0.15  # queue the rest just before the first part ends
    if wait > 0:
        time.sleep(wait)
    current = store.get("cw_meetings", meeting["id"], user_id) or {}
    if _speaking_until(current) == 0 or current.get("status") != "active":
        return "sent"  # they interrupted (barge-in cleared it) or the call ended
    recall.speak(meeting["bot_id"], base64.b64encode(tail).decode())
    _set_metric(store, user_id, meeting["id"], speaking_until=time.time() + mp3_seconds(tail))
    return "sent"


def _confirm_spoken_consent(store: Store, user_id: int, meeting: dict[str, Any], text: str,
                            turn_id: int) -> dict[str, Any]:
    """Handle the audible confirmation after link consent without retaining their words."""
    from coworker import meetings

    metrics = dict(meeting.get("metrics") or {})
    transcript = list(meeting.get("transcript") or [])
    # cw_turns is only a short-lived delivery buffer. Scrub the raw words now so
    # pre-confirmation speech is not retained in Ourogen's database.
    store.execute("UPDATE cw_turns SET text = %s WHERE meeting_id = %s AND user_id = %s AND claimed_by = %s",
                  (meetings.NOT_RECORDED, meeting["id"], user_id, turn_id))
    transcript.append({"speaker": "prospect", "text": meetings.NOT_RECORDED, "at": iso(), "redacted": True})
    declined = bool(meetings.LEAVE_RE.search(text) or meetings.CONSENT_NO_RE.search(text))
    confirmed = bool(meetings.CONSENT_YES_RE.search(text)) and not declined
    ended = False
    if confirmed:
        metrics["spoken_confirmation"] = "confirmed"
        metrics["spoken_confirmation_at"] = iso()
        reply, kind = "Thank you for confirming. What would you like to discuss?", "consent"
    elif declined:
        metrics["spoken_confirmation"] = "declined"
        metrics["recording_stopped"] = True
        reply, kind, ended = "Understood. I won't take notes, and I'll leave the call. Thank you.", "leave", True
    elif int(metrics.get("spoken_confirmation_asked", 0)) >= 1:
        metrics["spoken_confirmation"] = "not_confirmed"
        metrics["recording_stopped"] = True
        reply, kind, ended = "I didn't hear a clear confirmation, so I'll leave without taking notes. Thank you.", "leave", True
    else:
        metrics["spoken_confirmation_asked"] = 1
        reply, kind = "Before we continue, please say yes if you're okay with me participating and taking notes, or no and I'll leave.", "consent"
    transcript.append({"speaker": "coworker", "text": reply, "at": iso(), "kind": kind})
    values: dict[str, Any] = {"transcript": transcript, "metrics": metrics}
    if ended:
        values.update({"status": "ended", "ended_at": iso()})
    store.update("cw_meetings", meeting["id"], user_id, values)
    current = store.get("cw_meetings", meeting["id"], user_id)
    assert current is not None
    if ended:
        meetings.finish(store, user_id, meeting["id"])
        current = store.get("cw_meetings", meeting["id"], user_id) or current
    return {"reply": reply, "kind": kind, "meeting": current, "ended": ended, "latency_ms": 0}


def take_turn(store: Store, user_id: int, meeting_id: int, turn_id: int, wait: float | None = None) -> dict[str, Any] | None:
    """After the quiet window, answer everything said in this turn (unless a newer segment arrived)."""
    from coworker import meetings
    from coworker.connectors import recall
    from coworker.connectors.base import ConnectorError
    from coworker.voice import VoiceError

    time.sleep(silence_seconds() if wait is None else wait)
    text = claim(store, user_id, meeting_id, turn_id)
    if not text:
        return None
    started = time.monotonic()
    meeting = store.get("cw_meetings", meeting_id, user_id) or {}
    done = threading.Event()
    metrics = meeting.get("metrics") or {}
    pending = metrics.get("consent") == "pending" or metrics.get("spoken_confirmation") == "pending"

    def filler() -> None:
        if not done.wait(FILLER_AFTER):
            try:
                _say(store, user_id, meeting, "Good question." if text.rstrip().endswith("?") else "Got it.")
            except (ConnectorError, VoiceError):
                pass

    if not pending:  # never speak over someone's answer to the consent question
        threading.Thread(target=filler, name=f"call-filler-{meeting_id}", daemon=True).start()
    try:
        if metrics.get("spoken_confirmation") == "pending":
            result = _confirm_spoken_consent(store, user_id, meeting, text, turn_id)
        else:
            result = meetings.respond(store, user_id, meeting_id, text)
    finally:
        done.set()
    m = result["meeting"]
    try:
        audio_status = _say(store, user_id, m, result["reply"])
        _set_metric(store, user_id, meeting_id, audio_status=audio_status, audio_error="")
    except (ConnectorError, VoiceError) as exc:
        log.warning("couldn't speak on call %s: %s", meeting_id, exc)
        chat_sent = False
        if m.get("bot_id") and not result["ended"]:
            try:
                recall.send_chat(m["bot_id"], result["reply"])
                chat_sent = True
            except ConnectorError:
                log.warning("couldn't post fallback reply in meeting chat %s", meeting_id)
        _set_metric(store, user_id, meeting_id, audio_status="failed",
                    audio_error="Couldn't play audio in the meeting. " +
                    ("The reply was posted in meeting chat." if chat_sent else "The reply could not be posted in meeting chat either."))
    finally:
        if result["ended"] and m.get("bot_id"):
            try:
                recall.leave(m["bot_id"])
            except ConnectorError as exc:
                log.warning("couldn't leave meeting %s: %s", meeting_id, exc)
    elapsed = int((time.monotonic() - started) * 1000)
    metrics = (store.get("cw_meetings", meeting_id, user_id) or {}).get("metrics") or {}
    _set_metric(store, user_id, meeting_id, turn_ms=[*(metrics.get("turn_ms") or []), elapsed][-200:])
    return {**result, "turn_ms": elapsed}


def latency_summary(metrics: dict[str, Any]) -> dict[str, Any]:
    """p50/p95 of reply time (turn claimed to reply audio sent), in ms."""
    values = sorted(int(v) for v in metrics.get("turn_ms") or [])
    if not values:
        return {"turns": 0}

    def pct(p: float) -> int:
        return values[min(len(values) - 1, int(round(p * (len(values) - 1))))]

    return {"turns": len(values), "p50_ms": pct(0.5), "p95_ms": pct(0.95), "barge_ins": int(metrics.get("barge_ins", 0))}
