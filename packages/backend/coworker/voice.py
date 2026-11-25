"""Text-to-speech and voice cloning.

ElevenLabs remains the preferred provider for configured and cloned voices.
Meeting audio falls back to a local eSpeak/FFmpeg synthesizer when the
provider rejects a voice or is unavailable, so speaking is not coupled to a
paid ElevenLabs plan.
"""
from __future__ import annotations

import logging
import os
import shutil
import subprocess
from typing import Any

import requests

from coworker.errors import UserFacingError

API = "https://api.elevenlabs.io/v1"
TIMEOUT = 60
LOCAL_TIMEOUT = 30
log = logging.getLogger("coworker.voice")


class VoiceError(UserFacingError):
    pass


def _local_is_configured() -> bool:
    enabled = os.environ.get("COWORKER_LOCAL_TTS", "").strip().lower() in {"1", "true", "yes", "on"}
    return enabled and bool(shutil.which("espeak-ng")) and bool(shutil.which("ffmpeg"))


def is_configured() -> bool:
    return bool(os.environ.get("ELEVENLABS_API_KEY")) or _local_is_configured()


def _headers() -> dict[str, str]:
    return {"xi-api-key": os.environ.get("ELEVENLABS_API_KEY", "")}


def default_voice_id() -> str:
    return os.environ.get("ELEVENLABS_DEFAULT_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")


def _elevenlabs_tts(text: str, voice_id: str) -> bytes:
    resp = requests.post(
        f"{API}/text-to-speech/{voice_id}",
        params={"output_format": "mp3_44100_128"},
        headers={**_headers(), "Content-Type": "application/json"},
        json={"text": text[:2500], "model_id": os.environ.get("ELEVENLABS_MODEL_ID", "eleven_flash_v2_5")},
        timeout=TIMEOUT,
    )
    if resp.status_code != 200:
        raise VoiceError(f"Text-to-speech failed ({resp.status_code}): {resp.text[:200]}")
    if not resp.content:
        raise VoiceError("Text-to-speech returned no audio")
    return resp.content


def _local_tts(text: str) -> bytes:
    """Create a 128-kbps MP3 locally, without sending speech to another provider."""
    if not _local_is_configured():
        raise VoiceError("Local text-to-speech is unavailable")
    voice_name = os.environ.get("COWORKER_LOCAL_TTS_VOICE", "en-us").strip() or "en-us"
    try:
        speed = max(80, min(300, int(os.environ.get("COWORKER_LOCAL_TTS_SPEED", "165"))))
    except ValueError:
        speed = 165
    try:
        wav = subprocess.run(
            ["espeak-ng", "--stdout", "-v", voice_name, "-s", str(speed), text[:2500]],
            check=True,
            capture_output=True,
            timeout=LOCAL_TIMEOUT,
        ).stdout
        mp3 = subprocess.run(
            [
                "ffmpeg", "-hide_banner", "-loglevel", "error", "-f", "wav", "-i", "pipe:0",
                "-ar", "44100", "-ac", "1", "-codec:a", "libmp3lame", "-b:a", "128k",
                "-f", "mp3", "pipe:1",
            ],
            input=wav,
            check=True,
            capture_output=True,
            timeout=LOCAL_TIMEOUT,
        ).stdout
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        raise VoiceError("Local text-to-speech failed") from exc
    if not mp3:
        raise VoiceError("Local text-to-speech returned no audio")
    return mp3


def tts(text: str, voice_id: str | None = None) -> bytes:
    """MP3 audio, preferring ElevenLabs and falling back to local synthesis."""
    text = text.strip()
    if not text:
        raise VoiceError("Text-to-speech requires text")
    errors: list[str] = []
    if os.environ.get("ELEVENLABS_API_KEY"):
        candidates: list[str] = []
        for candidate in (voice_id, default_voice_id()):
            if candidate and candidate not in candidates:
                candidates.append(candidate)
        for candidate in candidates:
            try:
                return _elevenlabs_tts(text, candidate)
            except VoiceError as exc:
                errors.append(str(exc))
                log.warning("ElevenLabs TTS unavailable for voice %s; trying fallback: %s", candidate, exc)
    if _local_is_configured():
        try:
            return _local_tts(text)
        except VoiceError as exc:
            errors.append(str(exc))
            log.warning("Local TTS unavailable: %s", exc)
    if errors:
        raise VoiceError("Text-to-speech is unavailable: " + "; ".join(errors[:2]))
    raise VoiceError("Text-to-speech is not configured")


def clone(name: str, files: list[tuple[str, bytes, str]], description: str = "") -> str:
    """Create an instant voice clone from samples. Returns the voice id."""
    resp = requests.post(
        f"{API}/voices/add",
        headers=_headers(),
        data={"name": name, "description": description},
        files=[("files", (fname, data, mime)) for fname, data, mime in files],
        timeout=TIMEOUT,
    )
    if resp.status_code != 200:
        raise VoiceError(f"Voice cloning failed ({resp.status_code}): {resp.text[:200]}")
    body: dict[str, Any] = resp.json()
    return str(body.get("voice_id", ""))


def delete(voice_id: str) -> bool:
    if not voice_id:
        return False
    resp = requests.delete(f"{API}/voices/{voice_id}", headers=_headers(), timeout=TIMEOUT)
    return resp.status_code in (200, 204, 404)
