"""Tests for authentication endpoints."""


def test_register_missing_email(client):
    resp = client.post("/auth/register", json={"password": "password123"})
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_register_missing_password(client):
    resp = client.post("/auth/register", json={"email": "test@example.com"})
    assert resp.status_code == 400


def test_register_short_password(client):
    resp = client.post("/auth/register", json={"email": "t@e.com", "password": "short"})
    assert resp.status_code == 400


def test_register_success(client):
    resp = client.post("/auth/register", json={"email": "new@example.com", "password": "password123"})
    # No DB in the test client, so this surfaces as a clean 503 rather than a fake token.
    assert resp.status_code == 503


def test_login_missing_credentials(client):
    resp = client.post("/auth/login", json={})
    assert resp.status_code == 400


def test_login_no_db(client):
    resp = client.post("/auth/login", json={"email": "x@x.com", "password": "password123"})
    assert resp.status_code in (401, 503)


def test_me_without_token(client):
    resp = client.get("/auth/me")
    assert resp.status_code == 401


def test_me_with_token(client, auth_headers):
    resp = client.get("/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert "userId" in resp.get_json()


def test_google_login_missing_credential(client):
    resp = client.post("/auth/google", json={})
    assert resp.status_code == 400


def test_google_login_not_configured(client, monkeypatch):
    monkeypatch.delenv("GOOGLE_CLIENT_ID", raising=False)
    resp = client.post("/auth/google", json={"credential": "fake"})
    assert resp.status_code == 503


def test_google_login_invalid_credential(client, monkeypatch):
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "test-client-id")
    resp = client.post("/auth/google", json={"credential": "not-a-real-jwt"})
    assert resp.status_code == 401


def test_google_login_success(client, monkeypatch):
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "test-client-id")

    from api_endpoints.auth import handler

    def fake_verify(credential, request, audience):
        assert credential == "valid-token"
        assert audience == "test-client-id"
        return {"email": "googleuser@example.com", "email_verified": True, "name": "Google User"}

    monkeypatch.setattr(handler.google_id_token, "verify_oauth2_token", fake_verify)
    resp = client.post("/auth/google", json={"credential": "valid-token"})
    # No DB in the test client, so this surfaces as a clean 503 rather than a fake token.
    assert resp.status_code == 503
