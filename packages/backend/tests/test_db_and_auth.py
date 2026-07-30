"""Tests for the DB helpers and auth/document edge cases.

The DB layer talks to MySQL, which isn't available in CI, so these tests drive
the helpers with a lightweight fake connection/cursor rather than a real DB.
"""
from __future__ import annotations

import pytest

from database import db


class FakeCursor:
    def __init__(self, fetch_result=None, lastrowid=None):
        self._fetch_result = fetch_result
        self.lastrowid = lastrowid
        self.executed: list[tuple] = []
        self.closed = False

    def execute(self, sql, params=None):
        self.executed.append((sql, params))

    def fetchone(self):
        return self._fetch_result

    def close(self):
        self.closed = True


class FakeConnection:
    def __init__(self, cursor):
        self._cursor = cursor

    def cursor(self, dictionary=False):
        return self._cursor

    def close(self):
        pass


def test_get_user_by_email_found():
    row = {"id": 7, "email": "a@b.com"}
    cur = FakeCursor(fetch_result=row)
    cnx = FakeConnection(cur)
    assert db.get_user_by_email(cnx, "a@b.com") == row
    assert cur.closed is True
    # Query is parameterized — email is bound, never interpolated.
    sql, params = cur.executed[0]
    assert params == ("a@b.com",)


def test_get_user_by_email_missing():
    cur = FakeCursor(fetch_result=None)
    assert db.get_user_by_email(FakeConnection(cur), "none@x.com") is None


def test_create_user_returns_new_id():
    cur = FakeCursor(lastrowid=42)
    new_id = db.create_user(FakeConnection(cur), "a@b.com", "hash", "Alice")
    assert new_id == 42
    assert cur.closed is True
    sql, params = cur.executed[0]
    assert params == ("a@b.com", "hash", "Alice")


def test_get_connection_without_mysql(monkeypatch):
    """When the driver isn't installed, get_connection raises a clear error."""
    monkeypatch.setattr(db, "MYSQL_AVAILABLE", False)
    with pytest.raises(RuntimeError, match="mysql-connector-python"):
        db.get_connection()


# --- auth handler edge cases (the DB-unavailable fallback branches) ---

def test_register_missing_fields(client):
    assert client.post("/auth/register", json={}).status_code == 400


def test_register_short_password(client):
    resp = client.post("/auth/register", json={"email": "a@b.com", "password": "short"})
    assert resp.status_code == 400


def test_register_service_unavailable_without_db(client):
    """No DB reachable -> register surfaces a 503, not a fake fallback token.

    The fallback this test originally asserted was removed in b455823
    ("bug fix: mysql") because it handed out tokens for users that were
    never actually created, which left the browser holding a stale JWT.
    """
    resp = client.post(
        "/auth/register", json={"email": "new@x.com", "password": "longenough"}
    )
    assert resp.status_code == 503


def test_login_missing_fields(client):
    assert client.post("/auth/login", json={}).status_code == 400


def test_login_service_unavailable_without_db(client):
    """No DB reachable -> login surfaces a 503, not a 500."""
    resp = client.post("/auth/login", json={"email": "a@b.com", "password": "whatever"})
    assert resp.status_code == 503


def test_register_success_with_db(client, monkeypatch):
    """Happy path: no existing user, create_user issues id, real bcrypt hash."""
    from database import db as db_mod

    monkeypatch.setattr(db_mod, "get_connection", lambda: FakeConnection(FakeCursor()))
    monkeypatch.setattr(db_mod, "get_user_by_email", lambda cnx, email: None)
    monkeypatch.setattr(db_mod, "create_user", lambda cnx, e, h, n: 99)

    resp = client.post(
        "/auth/register", json={"email": "New@X.com", "password": "longenough", "name": "N"}
    )
    assert resp.status_code == 201
    assert resp.get_json()["userId"] == 99


def test_register_email_already_exists(client, monkeypatch):
    from database import db as db_mod

    monkeypatch.setattr(db_mod, "get_connection", lambda: FakeConnection(FakeCursor()))
    monkeypatch.setattr(db_mod, "get_user_by_email", lambda cnx, email: {"id": 1})

    resp = client.post(
        "/auth/register", json={"email": "dup@x.com", "password": "longenough"}
    )
    assert resp.status_code == 409


def test_login_success_with_db(client, monkeypatch):
    """Real bcrypt round-trip: hash a password, then log in with it."""
    from api_endpoints.auth import handler as auth_handler
    from database import db as db_mod

    pw = "correct-horse"
    hashed = auth_handler._hash_password(pw)
    user = {"id": 5, "password_hash": hashed}

    monkeypatch.setattr(db_mod, "get_connection", lambda: FakeConnection(FakeCursor()))
    monkeypatch.setattr(db_mod, "get_user_by_email", lambda cnx, email: user)

    resp = client.post("/auth/login", json={"email": "a@b.com", "password": pw})
    assert resp.status_code == 200
    assert resp.get_json()["userId"] == 5


def test_login_wrong_password(client, monkeypatch):
    from api_endpoints.auth import handler as auth_handler
    from database import db as db_mod

    user = {"id": 5, "password_hash": auth_handler._hash_password("right")}
    monkeypatch.setattr(db_mod, "get_connection", lambda: FakeConnection(FakeCursor()))
    monkeypatch.setattr(db_mod, "get_user_by_email", lambda cnx, email: user)

    resp = client.post("/auth/login", json={"email": "a@b.com", "password": "wrong"})
    assert resp.status_code == 401


def test_me_requires_auth(client):
    assert client.get("/auth/me").status_code == 401


def test_me_with_token(client, auth_headers):
    resp = client.get("/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["userId"] == "1"


# --- document handler edge cases ---
#
# Every /api/documents/* route is @require_auth, so these all need
# auth_headers — otherwise the request never reaches the handler body
# and every assertion below would just be checking for 401.

def test_upload_no_file(client, auth_headers):
    resp = client.post("/api/documents/upload", headers=auth_headers)
    assert resp.status_code == 400


def test_get_document_not_found(client, auth_headers, monkeypatch):
    from api_endpoints.documents import handler as doc_handler

    monkeypatch.setattr(doc_handler, "get_connection", lambda: FakeConnection(FakeCursor()))
    monkeypatch.setattr(doc_handler, "get_document_by_uuid", lambda cnx, user_id, doc_id: None)

    resp = client.get("/api/documents/nope", headers=auth_headers)
    assert resp.status_code == 404


def test_delete_document_not_found(client, auth_headers, monkeypatch):
    from api_endpoints.documents import handler as doc_handler

    monkeypatch.setattr(doc_handler, "get_connection", lambda: FakeConnection(FakeCursor()))
    monkeypatch.setattr(doc_handler, "get_document_by_uuid", lambda cnx, user_id, doc_id: None)

    resp = client.delete("/api/documents/nope", headers=auth_headers)
    assert resp.status_code == 404


def test_ask_document_not_found(client, auth_headers):
    """ask_document doesn't look the doc up — it just asks the RAG layer to
    retrieve context scoped to that id. For an id nothing was ever indexed
    under, retrieve_context comes back empty and query_documents returns a
    graceful "not found" answer with 200, not a 404 (see services/rag.py)."""
    resp = client.post("/api/documents/nope/ask", json={"question": "hi"}, headers=auth_headers)
    assert resp.status_code == 200
    assert "could not find" in resp.get_json()["answer"].lower()


def test_upload_unsupported_type(client, auth_headers):
    import io

    data = {"file": (io.BytesIO(b"binary"), "x.exe", "application/octet-stream")}
    resp = client.post(
        "/api/documents/upload", data=data, content_type="multipart/form-data", headers=auth_headers
    )
    assert resp.status_code == 400


def test_upload_and_ask_success(client, auth_headers, monkeypatch):
    """Happy path with RAG + DB mocked: upload a .txt, then ask a question."""
    import io

    from api_endpoints.documents import handler as doc_handler

    store: dict[str, dict] = {}

    def fake_create_document(cnx, user_id, doc_id, filename, chunk_count, folder_id, chat_id):
        store[doc_id] = {
            "id": doc_id,
            "filename": filename,
            "chunks": chunk_count,
            "folder_id": folder_id,
            "chat_id": chat_id,
        }

    monkeypatch.setattr(doc_handler, "get_connection", lambda: FakeConnection(FakeCursor()))
    monkeypatch.setattr(doc_handler, "create_document", fake_create_document)
    monkeypatch.setattr(doc_handler, "get_documents", lambda cnx, user_id, folder_id, chat_id: list(store.values()))
    monkeypatch.setattr(doc_handler, "get_document_by_uuid", lambda cnx, user_id, doc_id: store.get(doc_id))
    monkeypatch.setattr(doc_handler, "db_delete_document", lambda cnx, user_id, doc_id: store.pop(doc_id, None))
    monkeypatch.setattr(doc_handler, "ingest_document", lambda doc_id, file_path: 3)
    monkeypatch.setattr(
        doc_handler,
        "get_connection",
        lambda: FakeConnection(FakeCursor()),
    )
    monkeypatch.setattr(doc_handler, "create_document", lambda *args: 1)
    monkeypatch.setattr(
        doc_handler, "query_documents", lambda question, doc_ids, model: "the answer"
    )

    data = {"file": (io.BytesIO(b"hello world"), "notes.txt", "text/plain")}
    up = client.post(
        "/api/documents/upload", data=data, content_type="multipart/form-data", headers=auth_headers
    )
    assert up.status_code == 201
    doc_id = up.get_json()["id"]
    assert up.get_json()["chunks"] == 3

    # It now appears in the listing and is fetchable.
    listing = client.get("/api/documents", headers=auth_headers).get_json()["documents"]
    assert any(d["id"] == doc_id for d in listing)
    assert client.get(f"/api/documents/{doc_id}", headers=auth_headers).status_code == 200

    ask = client.post(f"/api/documents/{doc_id}/ask", json={"question": "what?"}, headers=auth_headers)
    assert ask.status_code == 200
    assert ask.get_json()["answer"] == "the answer"

    # Missing question is a 400 even for a real doc.
    assert client.post(f"/api/documents/{doc_id}/ask", json={}, headers=auth_headers).status_code == 400

    # And it can be deleted.
    assert client.delete(f"/api/documents/{doc_id}", headers=auth_headers).status_code == 200


def test_upload_ingest_failure_returns_500(client, auth_headers, monkeypatch):
    import io

    from api_endpoints.documents import handler as doc_handler

    def boom(doc_id, file_path):
        raise RuntimeError("parse failed")

    monkeypatch.setattr(doc_handler, "UPLOAD_FOLDER", tmp_path)
    monkeypatch.setattr(doc_handler, "ingest_document", boom)
    data = {"file": (io.BytesIO(b"hi"), "notes.txt", "text/plain")}
    resp = client.post(
        "/api/documents/upload", data=data, content_type="multipart/form-data", headers=auth_headers
    )
    assert resp.status_code == 500
