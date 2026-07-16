"""Tests for chat endpoints."""
from __future__ import annotations

import datetime
from unittest.mock import MagicMock, patch


def _mock_cnx(fetchall=None, fetchone=None, lastrowid=1, rowcount=1):
    cursor = MagicMock()
    cursor.fetchall.return_value = fetchall if fetchall is not None else []
    cursor.fetchone.return_value = fetchone
    cursor.lastrowid = lastrowid
    cursor.rowcount = rowcount
    cnx = MagicMock()
    cnx.cursor.return_value = cursor
    return cnx


def test_chat_stream_missing_message(client, auth_headers):
    resp = client.post("/api/chat/stream", json={}, headers=auth_headers)
    assert resp.status_code == 400


def test_chat_stream_no_auth(client):
    resp = client.post("/api/chat/stream", json={"message": "hi"})
    assert resp.status_code == 401


def test_chat_stream_new_session(client, auth_headers):
    with patch("api_endpoints.chat.handler.get_connection", return_value=_mock_cnx()):
        resp = client.post(
            "/api/chat/stream", json={"message": "hello"}, headers=auth_headers,
        )
        body = resp.get_data(as_text=True)
    assert resp.status_code == 200
    assert "session_id" in body


def test_chat_stream_existing_session_not_found(client, auth_headers):
    with patch(
        "api_endpoints.chat.handler.get_connection",
        return_value=_mock_cnx(fetchone=None),
    ):
        resp = client.post(
            "/api/chat/stream",
            json={"message": "hi", "session_id": 1},
            headers=auth_headers,
        )
    assert resp.status_code == 404


def test_chat_stream_existing_session(client, auth_headers):
    chat_row = {"id": 1, "name": "New Chat", "created_at": datetime.datetime(2024, 1, 1)}
    with patch(
        "api_endpoints.chat.handler.get_connection",
        return_value=_mock_cnx(fetchone=chat_row),
    ):
        resp = client.post(
            "/api/chat/stream",
            json={"message": "hi", "session_id": 1},
            headers=auth_headers,
        )
        body = resp.get_data(as_text=True)
    assert resp.status_code == 200
    # No new session should be announced when continuing an existing chat.
    assert "session_id" not in body


def test_chat_stream_injects_document_context(client, auth_headers):
    """Documents attached to this chat should be retrieved and fed to the
    model as context, scoped only to that chat's own uploads."""
    chat_row = {"id": 1, "name": "Existing Topic", "created_at": datetime.datetime(2024, 1, 1)}
    docs = [{"id": "doc-uuid-1"}]
    captured = {}

    def fake_stream(message, cwd=".", model="claude-sonnet-4-6", on_text=None):
        captured["message"] = message
        if on_text:
            on_text("An answer.")
        yield 'event: text\ndata: {"type": "text", "text": "An answer."}\n\n'

    with patch(
        "api_endpoints.chat.handler.get_connection",
        return_value=_mock_cnx(fetchone=chat_row),
    ), patch(
        "api_endpoints.chat.handler.get_documents", return_value=docs,
    ), patch(
        "api_endpoints.chat.handler.retrieve_context", return_value="relevant chunk",
    ) as mock_retrieve, patch(
        "api_endpoints.chat.handler.stream_agent_response", side_effect=fake_stream,
    ):
        resp = client.post(
            "/api/chat/stream",
            json={"message": "hi", "session_id": 1},
            headers=auth_headers,
        )
        resp.get_data(as_text=True)
    assert resp.status_code == 200
    mock_retrieve.assert_called_once_with("hi", doc_ids=["doc-uuid-1"])
    assert "relevant chunk" in captured["message"]
    assert "hi" in captured["message"]


def test_chat_stream_no_documents_skips_context(client, auth_headers):
    chat_row = {"id": 1, "name": "Existing Topic", "created_at": datetime.datetime(2024, 1, 1)}
    captured = {}

    def fake_stream(message, cwd=".", model="claude-sonnet-4-6", on_text=None):
        captured["message"] = message
        yield 'event: done\ndata: {"type": "done"}\n\n'

    with patch(
        "api_endpoints.chat.handler.get_connection",
        return_value=_mock_cnx(fetchone=chat_row, fetchall=[]),
    ), patch(
        "api_endpoints.chat.handler.retrieve_context",
    ) as mock_retrieve, patch(
        "api_endpoints.chat.handler.stream_agent_response", side_effect=fake_stream,
    ):
        resp = client.post(
            "/api/chat/stream",
            json={"message": "hi", "session_id": 1},
            headers=auth_headers,
        )
        resp.get_data(as_text=True)
    assert captured["message"] == "hi"
    mock_retrieve.assert_not_called()


def test_create_session(client, auth_headers):
    with patch("api_endpoints.chat.handler.get_connection", return_value=_mock_cnx(lastrowid=7)):
        resp = client.post("/api/chat/sessions", headers=auth_headers)
    assert resp.status_code == 201
    assert resp.get_json()["sessionId"] == "7"


def test_create_session_no_auth(client):
    resp = client.post("/api/chat/sessions")
    assert resp.status_code == 401


def test_search_missing_query(client, auth_headers):
    resp = client.get("/api/chat/search", headers=auth_headers)
    assert resp.status_code == 400


def test_search_no_auth(client):
    resp = client.get("/api/chat/search?q=hello")
    assert resp.status_code == 401


def test_search_returns_results(client, auth_headers):
    rows = [
        {
            "id": 1,
            "name": "Deploy Pipeline Help",
            "created_at": datetime.datetime(2024, 1, 1),
            "content": "How do I fix my CI pipeline? " + "x" * 200,
        },
    ]
    with patch(
        "api_endpoints.chat.handler.get_connection",
        return_value=_mock_cnx(fetchall=rows),
    ):
        resp = client.get("/api/chat/search?q=pipeline", headers=auth_headers)
    assert resp.status_code == 200
    results = resp.get_json()["results"]
    assert results[0]["id"] == "1"
    assert results[0]["title"] == "Deploy Pipeline Help"
    assert results[0]["snippet"].endswith("...")
    assert len(results[0]["snippet"]) == 163  # 160 chars + "..."


def test_search_dedupes_multiple_matching_messages_per_chat(client, auth_headers):
    rows = [
        {"id": 1, "name": "Chat A", "created_at": datetime.datetime(2024, 1, 1), "content": "first match"},
        {"id": 1, "name": "Chat A", "created_at": datetime.datetime(2024, 1, 1), "content": "second match"},
    ]
    with patch(
        "api_endpoints.chat.handler.get_connection",
        return_value=_mock_cnx(fetchall=rows),
    ):
        resp = client.get("/api/chat/search?q=match", headers=auth_headers)
    results = resp.get_json()["results"]
    assert len(results) == 1
    assert results[0]["snippet"] == "first match"


def test_search_title_only_match_has_no_snippet(client, auth_headers):
    rows = [
        {"id": 2, "name": "Budget Planning", "created_at": datetime.datetime(2024, 1, 1), "content": None},
    ]
    with patch(
        "api_endpoints.chat.handler.get_connection",
        return_value=_mock_cnx(fetchall=rows),
    ):
        resp = client.get("/api/chat/search?q=budget", headers=auth_headers)
    results = resp.get_json()["results"]
    assert results[0]["snippet"] is None


def test_search_chats_escapes_like_wildcards():
    from database.db import search_chats

    cnx = _mock_cnx(fetchall=[])
    search_chats(cnx, user_id=1, query="50%_off")
    executed_sql, params = cnx.cursor.return_value.execute.call_args.args
    assert params[0] == "%50\\%\\_off%"


def test_search_chats_is_case_insensitive():
    from database.db import search_chats

    cnx = _mock_cnx(fetchall=[])
    search_chats(cnx, user_id=1, query="BuDgEt")
    executed_sql, params = cnx.cursor.return_value.execute.call_args.args
    assert params[0] == "%budget%"
    assert "LOWER(" in executed_sql


def test_chat_stream_retitles_existing_untitled_session(client, auth_headers):
    """A prior attempt may have failed before producing a reply, leaving the
    chat named 'New Chat' — a later successful retry should still title it."""
    chat_row = {"id": 1, "name": "New Chat", "created_at": datetime.datetime(2024, 1, 1)}

    def fake_stream(message, cwd=".", model="claude-sonnet-4-6", on_text=None):
        if on_text:
            on_text("Hello!")
        yield 'event: text\ndata: {"type": "text", "text": "Hello!"}\n\n'

    with patch(
        "api_endpoints.chat.handler.get_connection",
        return_value=_mock_cnx(fetchone=chat_row),
    ), patch(
        "api_endpoints.chat.handler.stream_agent_response", side_effect=fake_stream,
    ), patch(
        "api_endpoints.chat.handler.generate_chat_title", return_value="Friendly Greeting",
    ):
        resp = client.post(
            "/api/chat/stream",
            json={"message": "hi", "session_id": 1},
            headers=auth_headers,
        )
        body = resp.get_data(as_text=True)
    assert resp.status_code == 200
    assert "Friendly Greeting" in body
    assert '"type": "title"' in body


def test_chat_stream_does_not_retitle_named_session(client, auth_headers):
    chat_row = {"id": 1, "name": "Existing Topic", "created_at": datetime.datetime(2024, 1, 1)}

    def fake_stream(message, cwd=".", model="claude-sonnet-4-6", on_text=None):
        if on_text:
            on_text("More info.")
        yield 'event: text\ndata: {"type": "text", "text": "More info."}\n\n'

    with patch(
        "api_endpoints.chat.handler.get_connection",
        return_value=_mock_cnx(fetchone=chat_row),
    ), patch(
        "api_endpoints.chat.handler.stream_agent_response", side_effect=fake_stream,
    ), patch(
        "api_endpoints.chat.handler.generate_chat_title",
    ) as mock_title:
        resp = client.post(
            "/api/chat/stream",
            json={"message": "more", "session_id": 1},
            headers=auth_headers,
        )
        resp.get_data(as_text=True)
    mock_title.assert_not_called()


def test_chat_missing_message(client):
    resp = client.post("/api/chat", json={})
    assert resp.status_code == 400


def test_chat_no_api_key(client):
    resp = client.post("/api/chat", json={"message": "hello"})
    assert resp.status_code in (200, 500)


def test_list_sessions_no_auth(client):
    resp = client.get("/api/chat/sessions")
    assert resp.status_code == 401


def test_list_sessions(client, auth_headers):
    chats = [{"id": 1, "name": "New Chat", "created_at": datetime.datetime(2024, 1, 1)}]
    with patch(
        "api_endpoints.chat.handler.get_connection",
        return_value=_mock_cnx(fetchall=chats),
    ):
        resp = client.get("/api/chat/sessions", headers=auth_headers)
    assert resp.status_code == 200
    sessions = resp.get_json()["sessions"]
    assert sessions[0]["id"] == "1"
    assert sessions[0]["title"] == "New Chat"


def test_get_session(client, auth_headers):
    chat_row = {"id": 1, "name": "New Chat", "created_at": datetime.datetime(2024, 1, 1)}
    messages = [
        {"role": "user", "content": "hi", "created_at": datetime.datetime(2024, 1, 1)},
    ]
    with patch(
        "api_endpoints.chat.handler.get_connection",
        return_value=_mock_cnx(fetchone=chat_row, fetchall=messages),
    ):
        resp = client.get("/api/chat/sessions/1", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["sessionId"] == "1"
    assert body["messages"][0]["content"] == "hi"


def test_get_session_not_found(client, auth_headers):
    with patch(
        "api_endpoints.chat.handler.get_connection",
        return_value=_mock_cnx(fetchone=None),
    ):
        resp = client.get("/api/chat/sessions/999", headers=auth_headers)
    assert resp.status_code == 404


def test_get_session_no_auth(client):
    resp = client.get("/api/chat/sessions/1")
    assert resp.status_code == 401


def test_delete_session(client, auth_headers):
    with patch("api_endpoints.chat.handler.get_connection", return_value=_mock_cnx()):
        resp = client.delete("/api/chat/sessions/1", headers=auth_headers)
    assert resp.status_code == 200


def test_delete_session_no_auth(client):
    resp = client.delete("/api/chat/sessions/1")
    assert resp.status_code == 401
