"""Smoke tests for Slack bot helpers — no Slack/Anthropic credentials needed."""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch
import os


def test_extract_query_strips_mention():
    os.environ.setdefault("SLACK_BOT_TOKEN", "xoxb-fake")
    os.environ.setdefault("SLACK_SIGNING_SECRET", "fake")
    os.environ.setdefault("ANTHROPIC_API_KEY", "sk-ant-fake")
    import importlib, sys
    for mod in list(sys.modules):
        if "slack_bot" in mod or (mod.startswith("app") and "bots" in str(sys.modules[mod])):
            del sys.modules[mod]
    sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent.parent))
    with patch("slack_bolt.App"):
        with patch("anthropic.Anthropic"):
            import app as bot
    result = bot.extract_query("<@U12345> explain this code")
    assert result == "explain this code"


def test_extract_query_empty_returns_none():
    os.environ.setdefault("SLACK_BOT_TOKEN", "xoxb-fake")
    os.environ.setdefault("SLACK_SIGNING_SECRET", "fake")
    os.environ.setdefault("ANTHROPIC_API_KEY", "sk-ant-fake")
    import sys
    sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent.parent))
    with patch("slack_bolt.App"):
        with patch("anthropic.Anthropic"):
            import app as bot
    result = bot.extract_query("<@U12345>   ")
    assert result is None


def test_trim_response_short():
    os.environ.setdefault("SLACK_BOT_TOKEN", "xoxb-fake")
    os.environ.setdefault("SLACK_SIGNING_SECRET", "fake")
    os.environ.setdefault("ANTHROPIC_API_KEY", "sk-ant-fake")
    import sys
    sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent.parent))
    with patch("slack_bolt.App"):
        with patch("anthropic.Anthropic"):
            import app as bot
    assert bot.trim_response("short") == "short"


def test_trim_response_long():
    os.environ.setdefault("SLACK_BOT_TOKEN", "xoxb-fake")
    os.environ.setdefault("SLACK_SIGNING_SECRET", "fake")
    os.environ.setdefault("ANTHROPIC_API_KEY", "sk-ant-fake")
    import sys
    sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent.parent))
    with patch("slack_bolt.App"):
        with patch("anthropic.Anthropic"):
            import app as bot
    long_text = "x" * 3000
    result = bot.trim_response(long_text)
    assert len(result) < 3000
    assert "truncated" in result


def _import_bot():
    os.environ.setdefault("SLACK_BOT_TOKEN", "xoxb-fake")
    os.environ.setdefault("SLACK_SIGNING_SECRET", "fake")
    os.environ.setdefault("ANTHROPIC_API_KEY", "sk-ant-fake")
    import sys
    sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent.parent))
    with patch("slack_bolt.App"):
        with patch("anthropic.Anthropic"):
            import app as bot
    return bot


def test_fetch_pending_approvals_calls_backend():
    bot = _import_bot()
    fake_resp = MagicMock()
    fake_resp.json.return_value = {"approvals": [{"id": "a1", "session_id": "s1", "action": "deploy"}]}
    fake_resp.raise_for_status.return_value = None
    with patch("requests.get", return_value=fake_resp) as mock_get:
        approvals = bot.fetch_pending_approvals()
    assert approvals == [{"id": "a1", "session_id": "s1", "action": "deploy"}]
    mock_get.assert_called_once()
    assert mock_get.call_args.kwargs["params"] == {"status": "pending"}


def test_resolve_approval_posts_decision():
    bot = _import_bot()
    fake_resp = MagicMock()
    fake_resp.json.return_value = {"id": "a1", "status": "approved"}
    fake_resp.raise_for_status.return_value = None
    with patch("requests.post", return_value=fake_resp) as mock_post:
        result = bot.resolve_approval("a1", True, "slack:alice")
    assert result["status"] == "approved"
    _, kwargs = mock_post.call_args
    assert kwargs["json"] == {"approved": True, "responder": "slack:alice"}


def test_build_approval_blocks_has_approve_and_deny_buttons():
    bot = _import_bot()
    approval = {"id": "a1", "session_id": "s1", "action": "rm -rf build/", "detail": "cleanup"}
    blocks = bot.build_approval_blocks(approval)
    action_ids = [
        el["action_id"]
        for block in blocks
        if block["type"] == "actions"
        for el in block["elements"]
    ]
    values = [
        el["value"]
        for block in blocks
        if block["type"] == "actions"
        for el in block["elements"]
    ]
    assert action_ids == ["approval_approve", "approval_deny"]
    assert values == ["a1", "a1"]
