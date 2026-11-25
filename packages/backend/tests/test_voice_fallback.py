"""Regression coverage for meeting voice fallback."""
from __future__ import annotations

import subprocess
from unittest.mock import MagicMock, patch

from coworker import voice


def _response(status: int, *, content: bytes = b"", text: str = "") -> MagicMock:
    response = MagicMock()
    response.status_code = status
    response.content = content
    response.text = text
    return response


def test_elevenlabs_payment_error_uses_local_audio(monkeypatch):
    monkeypatch.setenv("ELEVENLABS_API_KEY", "test-key")
    monkeypatch.setenv("COWORKER_LOCAL_TTS", "1")
    with patch("coworker.voice.requests.post", return_value=_response(402, text="paid_plan_required")), \
            patch("coworker.voice.shutil.which", return_value="/usr/bin/tool"), \
            patch("coworker.voice._local_tts", return_value=b"local-mp3") as local:
        assert voice.tts("Hello", "library-voice") == b"local-mp3"
    assert local.call_count == 1


def test_local_audio_is_encoded_for_recall(monkeypatch):
    monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
    monkeypatch.setenv("COWORKER_LOCAL_TTS", "1")
    completed = [
        subprocess.CompletedProcess(args=["espeak-ng"], returncode=0, stdout=b"wav"),
        subprocess.CompletedProcess(args=["ffmpeg"], returncode=0, stdout=b"mp3"),
    ]
    with patch("coworker.voice.shutil.which", return_value="/usr/bin/tool"), \
            patch("coworker.voice.subprocess.run", side_effect=completed) as run:
        assert voice.tts("Hello") == b"mp3"
    assert run.call_count == 2
    assert run.call_args_list[0].args[0][0] == "espeak-ng"
    assert run.call_args_list[1].args[0][0] == "ffmpeg"
    assert run.call_args_list[1].kwargs["input"] == b"wav"
