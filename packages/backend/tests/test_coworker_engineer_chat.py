"""The AI engineer, the code reviewer and the scorecard from chat (offline planner and tools)."""
from __future__ import annotations

from unittest.mock import patch

import pytest

from coworker import brain, executor, reports, tools
from coworker.connectors.devtools_demo import REPO
from coworker.store import Store


@pytest.fixture(autouse=True)
def _env(monkeypatch):
    monkeypatch.setenv("COWORKER_OFFLINE", "1")


@pytest.fixture
def s(tmp_path):
    store = Store(f"sqlite:///{tmp_path}/chat.db")
    store.create_coworker(1, "Natan Vidra", "natan@example.com", mode="demo")
    return store


def _text(events: list) -> str:
    return "\n".join(v for k, v in events if k == "text")


def test_take_a_ticket_from_chat_runs_it_and_shows_the_pr_card(s):
    with patch("coworker.reports.post", return_value=True) as post:
        events = list(brain.run_turn(s, 1, 7, "Take ACME-142 and open a PR when the tests pass"))
    text = _text(events)
    assert "Annual billing" in text and "Acceptance criteria" in text and "tests pass" in text and "slop score 100/100" in text
    cards = [v for k, v in events if k == "card"]
    action = s.get("cw_actions", cards[0]["id"], 1)
    assert action["type"] == "github.pr" and action["chat_id"] == 7 and action["status"] == "proposed"
    assert "is ready" in post.call_args.args[2]  # reported back into the chat that asked
    with patch("coworker.reports.post", return_value=True):
        executor.approve(s, 1, action["id"])
    assert reports.action_done(s.get("cw_actions", action["id"], 1), {"url": "https://x/pull/1"}).startswith("✅ Opened")


def test_review_from_chat(s):
    events = list(brain.run_turn(s, 1, None, "Review #37 please"))
    text = _text(events)
    assert f"**{REPO}#37**" in text and "high" in text and "needs a human look" in text
    assert any(k == "card" for k, _ in events)
    events = list(brain.run_turn(s, 1, 3, f"can you review {REPO}#37"))
    card = next(v for k, v in events if k == "card")
    assert s.get("cw_actions", card["id"], 1)["chat_id"] == 3
    s.update_coworker(1, mode="live")
    assert "Connect GitHub" in _text(list(brain.run_turn(s, 1, None, "review acme/api#1")))


def test_scorecard_from_chat(s):
    assert "Last 7 days" in _text(list(brain.run_turn(s, 1, None, "How much did you get done?")))
    assert "Last 30 days" in _text(list(brain.run_turn(s, 1, None, "show me the work you did this month")))


def test_engineer_task_tool_paths(s):
    ctx = tools.ToolContext(store=s, user_id=1, owner_message="")
    out, _ = tools.run("engineer_task", {"source": "jira:ACME-142"}, ctx)
    assert out["status"] == "planned"  # nobody typed it: plan only
    ctx = tools.ToolContext(store=s, user_id=1, owner_message="go", responsibility={"id": 1})
    assert tools.run("engineer_task", {"source": "jira:ACME-142"}, ctx)[0]["status"] == "planned"
    ctx = tools.ToolContext(store=s, user_id=1, owner_message="go")
    assert tools.run("engineer_task", {"source": "jira:ACME-142", "start": False}, ctx)[0]["status"] == "planned"
    assert "error" in tools.run("engineer_task", {"source": "trello:x"}, ctx)[0]
    with patch("coworker.reports.post", return_value=True) as post:
        stuck, _ = tools.run("engineer_task", {"text": "Add CSV export\n- returns a CSV", "repo": REPO},
                             tools.ToolContext(store=s, user_id=1, owner_message="go", chat_id=9))
    assert stuck["status"] == "needs_model" and "stopped work" in post.call_args.args[2]
    status, _ = tools.run("engineer_status", {}, ctx)
    assert {r["status"] for r in status} >= {"planned", "needs_model"}
    with patch("coworker.engineering.runs.start", side_effect=__import__("coworker.engineering.runs", fromlist=["RunError"]).RunError("nope")):
        out, _ = tools.run("engineer_task", {"source": "jira:ACME-142"}, ctx)
    assert out["status"] == "planned" and out["error"] == "nope"
    assert ctx.read_untrusted  # ticket text is someone else's words


def test_engineer_offline_errors_and_running(s):
    assert "Source must look like" not in _text(list(brain.run_turn(s, 1, None, "Take ZZZ-1 please")))  # unknown ticket
    with patch("coworker.tools._engineer_task", return_value=({"error": "boom"}, "x")):
        assert _text(list(brain.run_turn(s, 1, None, "work on ACME-142"))) == "boom"
    planned = {"run_id": 1, "goal": "g", "repo": REPO, "acceptance_criteria": ["c"], "plan": [{"task": "t", "files": ["a"]}]}
    with patch("coworker.tools._engineer_task", return_value=({**planned, "status": "running"}, "x")):
        assert "I'm working on it" in _text(list(brain.run_turn(s, 1, None, "work on ACME-142")))
    with patch("coworker.tools._engineer_task", return_value=({**planned, "status": "failed", "error": "tests broke"}, "x")):
        assert "tests broke" in _text(list(brain.run_turn(s, 1, None, "open a PR that adds dark mode")))


def test_action_done_texts():
    base = {"id": 1, "title": "T", "payload": {"repo": "a/b", "number": 2, "server": "linear", "tool": "create"}}
    assert "Posted the review on a/b#2" in reports.action_done({**base, "type": "github.review"}, {"url": "u"})
    assert "(u)" in reports.action_done({**base, "type": "jira.comment"}, {"url": "u"})
    assert "Ran create on linear" in reports.action_done({**base, "type": "mcp.call"}, {"output": "ok"})
    assert reports.action_done({**base, "type": "notion.page"}, {}) == "✅ Done: T"
