"""Tests for AnoteClient — uses respx to mock HTTP, no live server needed."""
from __future__ import annotations

import pytest
import respx
import httpx

from anote_sdk import AnoteClient, AnoteError
from anote_sdk.models import ChatResult


BASE = "http://localhost:5000"


@pytest.fixture
def client():
    return AnoteClient(api_key="test-token", base_url=BASE)


def test_constructor_requires_api_key():
    with pytest.raises(ValueError, match="api_key is required"):
        AnoteClient(api_key="")


def test_health(client):
    with respx.mock:
        respx.get(f"{BASE}/health").mock(
            return_value=httpx.Response(200, json={"status": "ok", "service": "anote-backend"})
        )
        result = client.health()
    assert result.status == "ok"
    assert result.service == "anote-backend"


def test_chat(client):
    with respx.mock:
        respx.post(f"{BASE}/api/chat").mock(
            return_value=httpx.Response(200, json={
                "response": "Hello world",
                "model": "claude-sonnet-4-6",
            })
        )
        result = client.chat("say hello")
    assert result.response == "Hello world"
    assert isinstance(result, ChatResult)


def test_chat_with_history(client):
    with respx.mock:
        route = respx.post(f"{BASE}/api/chat").mock(
            return_value=httpx.Response(200, json={"response": "done", "model": "claude-sonnet-4-6"})
        )
        from anote_sdk.models import ChatMessage

        result = client.chat("fix bug", history=[ChatMessage(role="user", content="earlier turn")])
    assert result.response == "done"
    assert route.called
    sent_body = route.calls[0].request.content
    assert b"earlier turn" in sent_body


def test_error_raises_anote_error(client):
    with respx.mock:
        respx.post(f"{BASE}/api/chat").mock(
            return_value=httpx.Response(401, json={"error": "Unauthorized"})
        )
        with pytest.raises(AnoteError) as exc_info:
            client.chat("hello")
    assert exc_info.value.status == 401


def test_list_sessions_empty(client):
    with respx.mock:
        respx.get(f"{BASE}/api/chat/sessions").mock(
            return_value=httpx.Response(200, json={"sessions": []})
        )
        sessions = client.list_sessions()
    assert sessions == []


def test_create_session(client):
    with respx.mock:
        respx.post(f"{BASE}/api/chat/sessions").mock(
            return_value=httpx.Response(201, json={"sessionId": "abc123"})
        )
        session_id = client.create_session()
    assert session_id == "abc123"


def test_get_session_messages(client):
    with respx.mock:
        respx.get(f"{BASE}/api/chat/sessions/abc123").mock(
            return_value=httpx.Response(
                200,
                json={"sessionId": "abc123", "messages": [{"role": "user", "content": "hi"}]},
            )
        )
        session = client.get_session_messages("abc123")
    assert session.session_id == "abc123"
    assert session.messages[0].content == "hi"


def test_delete_session(client):
    with respx.mock:
        respx.delete(f"{BASE}/api/chat/sessions/abc123").mock(
            return_value=httpx.Response(200, json={"deleted": True})
        )
        ok = client.delete_session("abc123")
    assert ok is True


def test_search(client):
    with respx.mock:
        respx.get(f"{BASE}/api/search").mock(
            return_value=httpx.Response(
                200,
                json={
                    "results": [
                        {"file": "app.py", "startLine": 1, "endLine": 5, "preview": "...", "score": 0.9}
                    ],
                    "query": "hello",
                    "cwd": "/project",
                },
            )
        )
        response = client.search("hello")
    assert response.query == "hello"
    assert response.results[0].file == "app.py"
    assert response.results[0].start_line == 1
