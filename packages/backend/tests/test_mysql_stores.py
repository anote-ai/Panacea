"""Unit tests for the MySQL persistence backends.

The stores open connections via database.db.get_connection, so we patch that
— no real MySQL needed (same approach as the auth helpers).
"""
from datetime import datetime
from unittest.mock import MagicMock

import pytest

from services.chat_sessions import MySQLChatSessionStore, chat_store_from_config
from services.document_store import MySQLDocumentStore, document_store_from_config

NOW = datetime(2026, 7, 10, 12, 0, 0)


def _patch_connection(monkeypatch, fetchone=None, fetchall=None, lastrowid=1, rowcount=1):
    cnx = MagicMock()
    cursor = MagicMock()
    cursor.lastrowid = lastrowid
    cursor.rowcount = rowcount
    if isinstance(fetchone, list):
        cursor.fetchone.side_effect = fetchone
    else:
        cursor.fetchone.return_value = fetchone
    cursor.fetchall.return_value = fetchall if fetchall is not None else []
    cnx.cursor.return_value = cursor
    monkeypatch.setattr("database.db.get_connection", lambda: cnx)
    return cnx, cursor


def _chat_row(**overrides):
    row = {
        "id": 7,
        "session_uuid": "abc-123",
        "name": "My Chat",
        "cwd": "/tmp",
        "model": "claude-sonnet-4-6",
        "user_id": 1,
        "created_at": NOW,
        "updated_at": NOW,
        "message_count": 2,
    }
    row.update(overrides)
    return row


# ── factory selection ─────────────────────────────────────────────────────────


def test_factories_select_backend_from_config(tmp_path):
    sqlite_config = {
        "PERSISTENCE_BACKEND": "sqlite",
        "CHAT_SESSION_DB_PATH": str(tmp_path / "c.sqlite3"),
        "DOCUMENT_METADATA_DB_PATH": str(tmp_path / "d.sqlite3"),
    }
    assert not isinstance(chat_store_from_config(sqlite_config), MySQLChatSessionStore)
    assert not isinstance(document_store_from_config(sqlite_config), MySQLDocumentStore)

    mysql_config = {"PERSISTENCE_BACKEND": "mysql"}
    assert isinstance(chat_store_from_config(mysql_config), MySQLChatSessionStore)
    assert isinstance(document_store_from_config(mysql_config), MySQLDocumentStore)


# ── chat store ────────────────────────────────────────────────────────────────


def test_create_session_inserts_user_scoped_chat(monkeypatch):
    # First fetchone: no existing session; second: the inserted row
    cnx, cursor = _patch_connection(monkeypatch, fetchone=[None, _chat_row()])
    session = MySQLChatSessionStore().create_session(
        session_id="abc-123", title="My Chat", cwd="/tmp", model="claude-sonnet-4-6", user_id=1
    )
    insert_sql, params = cursor.execute.call_args_list[1][0]
    assert "INSERT INTO chats" in insert_sql
    assert params == (1, "My Chat", "chat", "abc-123", "/tmp", "claude-sonnet-4-6")
    assert session["id"] == "abc-123"
    assert session["userId"] == 1
    assert session["messageCount"] == 2
    cnx.close.assert_called_once()


def test_list_sessions_filters_by_user(monkeypatch):
    _, cursor = _patch_connection(monkeypatch, fetchall=[_chat_row()])
    sessions = MySQLChatSessionStore().list_sessions(user_id=1)
    sql, params = cursor.execute.call_args[0]
    assert "WHERE c.user_id = %s" in sql
    assert params == (1,)
    assert sessions[0]["sessionId"] == "abc-123"


def test_list_sessions_anonymous_uses_null_filter(monkeypatch):
    _, cursor = _patch_connection(monkeypatch, fetchall=[])
    MySQLChatSessionStore().list_sessions()
    sql, params = cursor.execute.call_args[0]
    assert "WHERE c.user_id IS NULL" in sql
    assert params == ()


def test_add_message_inserts_and_touches_chat(monkeypatch):
    _, cursor = _patch_connection(monkeypatch, fetchone={"id": 7}, lastrowid=99)
    message = MySQLChatSessionStore().add_message(
        "abc-123", role="user", content="hello there", model="claude-sonnet-4-6"
    )
    insert_sql, insert_params = cursor.execute.call_args_list[1][0]
    assert "INSERT INTO messages" in insert_sql
    assert insert_params == (7, "user", "hello there", "claude-sonnet-4-6")
    update_sql, _ = cursor.execute.call_args_list[2][0]
    assert "UPDATE chats" in update_sql
    assert message["id"] == "99"


def test_add_message_unknown_session_raises(monkeypatch):
    _patch_connection(monkeypatch, fetchone=None)
    with pytest.raises(ValueError, match="unknown chat session"):
        MySQLChatSessionStore().add_message("missing", role="user", content="hi")


def test_get_messages_joins_on_session_uuid(monkeypatch):
    rows = [
        {"id": 1, "role": "user", "content": "hi", "model": None, "created_at": NOW},
        {"id": 2, "role": "assistant", "content": "hello", "model": "claude", "created_at": NOW},
    ]
    _, cursor = _patch_connection(monkeypatch, fetchall=rows)
    messages = MySQLChatSessionStore().get_messages("abc-123")
    sql, params = cursor.execute.call_args[0]
    assert "JOIN chats" in sql
    assert params == ("abc-123",)
    assert [m["role"] for m in messages] == ["user", "assistant"]
    assert messages[0]["model"] == ""


def test_delete_session_by_uuid(monkeypatch):
    _, cursor = _patch_connection(monkeypatch, rowcount=1)
    assert MySQLChatSessionStore().delete_session("abc-123") is True
    sql, params = cursor.execute.call_args[0]
    assert "DELETE FROM chats WHERE session_uuid" in sql
    assert params == ("abc-123",)


# ── document store ────────────────────────────────────────────────────────────


def _doc_row(**overrides):
    row = {
        "id": 3,
        "doc_uuid": "doc-1",
        "filename": "sample.txt",
        "path": "/tmp/doc-1.txt",
        "content_type": "text/plain",
        "chunk_count": 4,
        "user_id": None,
        "created_at": NOW,
        "updated_at": NOW,
    }
    row.update(overrides)
    return row


def test_save_document_upserts_by_uuid(monkeypatch):
    _, cursor = _patch_connection(monkeypatch, fetchone=_doc_row(user_id=1))
    document = MySQLDocumentStore().save_document(
        doc_id="doc-1",
        filename="sample.txt",
        path="/tmp/doc-1.txt",
        chunks=4,
        content_type="text/plain",
        user_id=1,
    )
    sql, params = cursor.execute.call_args_list[0][0]
    assert "INSERT INTO documents" in sql
    assert "ON DUPLICATE KEY UPDATE" in sql
    assert params == (1, "doc-1", "sample.txt", "/tmp/doc-1.txt", 4, "text/plain")
    assert document["id"] == "doc-1"
    assert document["chunks"] == 4


def test_list_documents_filters_by_user(monkeypatch):
    _, cursor = _patch_connection(monkeypatch, fetchall=[_doc_row()])
    MySQLDocumentStore().list_documents()
    sql, params = cursor.execute.call_args[0]
    assert "WHERE user_id IS NULL" in sql
    assert params == ()


def test_delete_document_returns_metadata(monkeypatch):
    _, cursor = _patch_connection(monkeypatch, fetchone=_doc_row())
    document = MySQLDocumentStore().delete_document("doc-1")
    assert document["filename"] == "sample.txt"
    delete_sql, params = cursor.execute.call_args[0]
    assert "DELETE FROM documents WHERE doc_uuid" in delete_sql
    assert params == ("doc-1",)


def test_delete_missing_document_returns_none(monkeypatch):
    _patch_connection(monkeypatch, fetchone=None)
    assert MySQLDocumentStore().delete_document("missing") is None
