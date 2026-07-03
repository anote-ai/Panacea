"""Tests for chat endpoints."""
import json
import re

from services.chat_sessions import ChatSessionStore
from services.streaming import sse_event


def test_chat_stream_missing_message(client):
    resp = client.post("/api/chat/stream", json={})
    assert resp.status_code == 400


def test_chat_missing_message(client):
    resp = client.post("/api/chat", json={})
    assert resp.status_code == 400


def test_chat_no_api_key(client):
    resp = client.post("/api/chat", json={"message": "hello"})
    assert resp.status_code in (200, 500)


def test_list_sessions(client):
    resp = client.get("/api/chat/sessions")
    assert resp.status_code == 200
    assert "sessions" in resp.get_json()


def test_create_session(client):
    resp = client.post("/api/chat/sessions")
    assert resp.status_code == 201
    assert "sessionId" in resp.get_json()


def test_get_session(client):
    sid = client.post("/api/chat/sessions").get_json()["sessionId"]
    resp = client.get(f"/api/chat/sessions/{sid}")
    assert resp.status_code == 200
    assert resp.get_json()["sessionId"] == sid
    assert resp.get_json()["messages"] == []


def test_get_session_not_found(client):
    resp = client.get("/api/chat/sessions/does-not-exist")
    assert resp.status_code == 404


def test_delete_session(client):
    sid = client.post("/api/chat/sessions").get_json()["sessionId"]
    resp = client.delete(f"/api/chat/sessions/{sid}")
    assert resp.status_code == 200
    assert resp.get_json()["ok"] is True


def test_session_store_persists_across_instances(tmp_path):
    db_path = tmp_path / "sessions.sqlite3"
    first = ChatSessionStore(db_path)
    session = first.create_session(title="First chat")
    first.add_message(session["id"], role="user", content="hello", model="claude")

    second = ChatSessionStore(db_path)
    assert second.get_session(session["id"])["messageCount"] == 1
    assert second.get_messages(session["id"])[0]["content"] == "hello"


def test_stream_chat_creates_session_and_persists_messages(client, monkeypatch):
    def fake_stream_agent_response(*, on_text=None, **kwargs):
        if on_text:
            on_text("hello back")
        yield sse_event("text", {"text": "hello back"})
        yield sse_event("done", {})

    monkeypatch.setattr(
        "api_endpoints.chat.handler.stream_agent_response",
        fake_stream_agent_response,
    )

    resp = client.post("/api/chat/stream", json={"message": "hello"})
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert '"type": "session_id"' in body
    assert '"type": "text"' in body

    match = re.search(r'data: ({"type": "session_id".*})', body)
    assert match
    session_id = json.loads(match.group(1))["session_id"]

    session_resp = client.get(f"/api/chat/sessions/{session_id}")
    assert session_resp.status_code == 200
    messages = session_resp.get_json()["messages"]
    assert [m["role"] for m in messages] == ["user", "assistant"]
    assert messages[1]["content"] == "hello back"
