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


def test_google_login_start_not_configured(client, monkeypatch):
    monkeypatch.delenv("GOOGLE_CLIENT_ID", raising=False)
    resp = client.get("/auth/google/login")
    assert resp.status_code == 503


def test_google_login_start_redirects_to_google(client, monkeypatch):
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "test-client-id")
    resp = client.get("/auth/google/login")
    assert resp.status_code == 302
    assert resp.headers["Location"].startswith("https://accounts.google.com/o/oauth2/v2/auth?")
    assert "client_id=test-client-id" in resp.headers["Location"]


def test_callback_google_denied(client):
    resp = client.get("/callback?error=access_denied")
    assert resp.status_code == 302
    assert "error=google_denied" in resp.headers["Location"]


def test_callback_missing_code(client):
    resp = client.get("/callback")
    assert resp.status_code == 302
    assert "error=missing_code" in resp.headers["Location"]


def test_callback_invalid_state(client):
    resp = client.get("/callback?code=abc&state=not-a-real-state")
    assert resp.status_code == 302
    assert "error=invalid_state" in resp.headers["Location"]


def _make_valid_state(app):
    from api_endpoints.auth.handler import _state_serializer
    with app.app_context():
        return _state_serializer().dumps("nonce")


def test_callback_not_configured(client, app, monkeypatch):
    monkeypatch.delenv("GOOGLE_CLIENT_ID", raising=False)
    monkeypatch.delenv("GOOGLE_CLIENT_SECRET", raising=False)
    state = _make_valid_state(app)
    resp = client.get(f"/callback?code=abc&state={state}")
    assert resp.status_code == 302
    assert "error=not_configured" in resp.headers["Location"]


def test_callback_success(client, app, monkeypatch):
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "test-client-id")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "test-client-secret")
    state = _make_valid_state(app)

    from api_endpoints.auth import handler

    class FakeTokenResponse:
        ok = True
        status_code = 200
        text = ""

        def json(self):
            return {"id_token": "fake-id-token"}

    def fake_post(url, data, timeout):
        assert url == handler.GOOGLE_TOKEN_URL
        assert data["code"] == "abc"
        return FakeTokenResponse()

    def fake_verify(id_token_str, request, audience, clock_skew_in_seconds=0):
        assert id_token_str == "fake-id-token"
        assert audience == "test-client-id"
        return {"email": "googleuser@example.com", "email_verified": True, "name": "Google User"}

    monkeypatch.setattr(handler.http_requests, "post", fake_post)
    monkeypatch.setattr(handler.google_id_token, "verify_oauth2_token", fake_verify)

    resp = client.get(f"/callback?code=abc&state={state}")
    # No DB in the test client, so this surfaces as a clean redirect-with-error
    # rather than a fake token.
    assert resp.status_code == 302
    assert "error=service_unavailable" in resp.headers["Location"]
