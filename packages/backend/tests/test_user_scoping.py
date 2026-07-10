"""User-scoping rules for chat sessions and documents (SQLite backend).

Logged-in users only see their own sessions/documents; anonymous requests
only see anonymous ones. Owned resources return 404 to everyone else.
"""
import io


def _other_user_headers(app, identity="2"):
    with app.app_context():
        from flask_jwt_extended import create_access_token
        token = create_access_token(identity=identity)
    return {"Authorization": f"Bearer {token}"}


# ── chat sessions ─────────────────────────────────────────────────────────────


def test_session_lists_are_scoped_per_user(client, auth_headers):
    anon_sid = client.post("/api/chat/sessions").get_json()["sessionId"]
    user_sid = client.post("/api/chat/sessions", headers=auth_headers).get_json()["sessionId"]

    anon_listed = {s["id"] for s in client.get("/api/chat/sessions").get_json()["sessions"]}
    assert anon_sid in anon_listed
    assert user_sid not in anon_listed

    user_listed = {
        s["id"]
        for s in client.get("/api/chat/sessions", headers=auth_headers).get_json()["sessions"]
    }
    assert user_sid in user_listed
    assert anon_sid not in user_listed


def test_owned_session_hidden_from_others(client, app, auth_headers):
    sid = client.post("/api/chat/sessions", headers=auth_headers).get_json()["sessionId"]

    assert client.get(f"/api/chat/sessions/{sid}").status_code == 404
    assert client.get(f"/api/chat/sessions/{sid}/messages").status_code == 404
    assert client.delete(f"/api/chat/sessions/{sid}").status_code == 404
    other = _other_user_headers(app)
    assert client.get(f"/api/chat/sessions/{sid}", headers=other).status_code == 404

    assert client.get(f"/api/chat/sessions/{sid}", headers=auth_headers).status_code == 200
    assert client.delete(f"/api/chat/sessions/{sid}", headers=auth_headers).status_code == 200


def test_anonymous_session_reachable_by_logged_in_user(client, auth_headers):
    sid = client.post("/api/chat/sessions").get_json()["sessionId"]
    assert client.get(f"/api/chat/sessions/{sid}", headers=auth_headers).status_code == 200


def test_stream_binds_new_session_to_user(client, app, auth_headers, monkeypatch):
    from services.streaming import sse_event

    def fake_stream_agent_response(*, on_text=None, **kwargs):
        if on_text:
            on_text("ok")
        yield sse_event("text", {"text": "ok"})
        yield sse_event("done", {})

    monkeypatch.setattr(
        "api_endpoints.chat.handler.stream_agent_response",
        fake_stream_agent_response,
    )

    resp = client.post("/api/chat/stream", json={"message": "hi"}, headers=auth_headers)
    assert resp.status_code == 200
    resp.get_data()  # drain the stream so messages are persisted

    sessions = client.get("/api/chat/sessions", headers=auth_headers).get_json()["sessions"]
    assert len(sessions) == 1
    assert sessions[0]["userId"] == 1


def test_stream_rejects_foreign_session(client, auth_headers):
    sid = client.post("/api/chat/sessions", headers=auth_headers).get_json()["sessionId"]
    resp = client.post("/api/chat/stream", json={"message": "hi", "session_id": sid})
    assert resp.status_code == 404


# ── documents ─────────────────────────────────────────────────────────────────


def _upload(client, headers=None):
    data = {"file": (io.BytesIO(b"Content."), "doc.txt")}
    return client.post(
        "/api/documents/upload",
        data=data,
        content_type="multipart/form-data",
        headers=headers or {},
    )


def test_document_lists_are_scoped_per_user(client, auth_headers, monkeypatch):
    monkeypatch.setattr("api_endpoints.documents.handler.ingest_document", lambda **kwargs: 1)

    anon_id = _upload(client).get_json()["id"]
    user_id = _upload(client, auth_headers).get_json()["id"]

    anon_listed = {d["id"] for d in client.get("/api/documents").get_json()["documents"]}
    assert anon_id in anon_listed
    assert user_id not in anon_listed

    user_listed = {
        d["id"]
        for d in client.get("/api/documents", headers=auth_headers).get_json()["documents"]
    }
    assert user_id in user_listed
    assert anon_id not in user_listed


def test_owned_document_hidden_from_others(client, app, auth_headers, monkeypatch):
    monkeypatch.setattr("api_endpoints.documents.handler.ingest_document", lambda **kwargs: 1)
    doc_id = _upload(client, auth_headers).get_json()["id"]

    assert client.get(f"/api/documents/{doc_id}").status_code == 404
    assert client.delete(f"/api/documents/{doc_id}").status_code == 404
    assert (
        client.post(f"/api/documents/{doc_id}/ask", json={"question": "?"}).status_code == 404
    )
    other = _other_user_headers(app)
    assert client.get(f"/api/documents/{doc_id}", headers=other).status_code == 404

    assert client.get(f"/api/documents/{doc_id}", headers=auth_headers).status_code == 200
    assert client.delete(f"/api/documents/{doc_id}", headers=auth_headers).status_code == 200
