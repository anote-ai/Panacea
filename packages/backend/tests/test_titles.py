"""Tests for chat title generation."""
from __future__ import annotations

from unittest.mock import patch

from services.titles import generate_chat_title


def test_generate_chat_title_success():
    with patch("services.titles.complete", return_value='"Deploy Pipeline Help"'):
        title = generate_chat_title("How do I fix my CI pipeline?")
    assert title == "Deploy Pipeline Help"


def test_generate_chat_title_falls_back_on_error():
    with patch("services.titles.complete", side_effect=RuntimeError("boom")):
        title = generate_chat_title("This is the first message of the chat")
    assert title == "This is the first message of the chat"


def test_generate_chat_title_falls_back_on_empty_response():
    with patch("services.titles.complete", return_value="   "):
        title = generate_chat_title("hello there")
    assert title == "hello there"


def test_generate_chat_title_empty_message_fallback():
    with patch("services.titles.complete", side_effect=RuntimeError("boom")):
        title = generate_chat_title("   ")
    assert title == "New chat"


def test_generate_chat_title_includes_assistant_reply_in_prompt():
    with patch("services.titles.complete", return_value="Deploy Pipeline Help") as mock_complete:
        generate_chat_title("How do I fix my CI pipeline?", "Check your YAML syntax first.")
    prompt = mock_complete.call_args.args[0]
    assert "How do I fix my CI pipeline?" in prompt
    assert "Check your YAML syntax first." in prompt


def test_generate_chat_title_uses_passed_model():
    with patch("services.titles.complete", return_value="Title") as mock_complete:
        generate_chat_title("hi", model="gpt-4o-mini")
    assert mock_complete.call_args.kwargs["model"] == "gpt-4o-mini"
