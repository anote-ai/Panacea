"""A production Coworker connection must not send Google to localhost."""
from __future__ import annotations

from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

from coworker.connectors import google


def test_production_uses_registered_login_callback_when_backend_url_is_local(
    client, auth_headers, monkeypatch,
):
    callback = "https://api.ourogen.ai/callback"
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("BACKEND_URL", "http://localhost:5000")
    monkeypatch.setenv("GOOGLE_COWORKER_REDIRECT_URI", "http://localhost:5000/api/coworker/connections/google/callback")
    monkeypatch.setenv("GOOGLE_OAUTH_REDIRECT_URI", callback)
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "client-id")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "secret")

    started = client.post("/api/coworker/connections/google/start", headers=auth_headers)
    assert started.status_code == 200
    auth = parse_qs(urlparse(started.get_json()["url"]).query)
    assert auth["redirect_uri"] == [callback]
    with patch("coworker.connectors.google.requests.post") as post:
        post.return_value.status_code = 200
        post.return_value.json.return_value = {"access_token": "t"}
        google.exchange_code("code")
    assert post.call_args.kwargs["data"]["redirect_uri"] == callback

    # Google returns to the shared callback; the signed Coworker state must
    # route to /finish, where the user's signed-in account is checked.
    returned = client.get(f"/callback?state={auth['state'][0]}&code=google-code")
    assert returned.status_code == 302
    parsed = urlparse(returned.headers["Location"])
    assert parsed.path == "/app/connect/finish"
    assert parse_qs(parsed.query)["provider"] == ["google"]


def test_production_rejects_local_callback_without_public_fallback(client, auth_headers, monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("BACKEND_URL", "http://localhost:5000")
    monkeypatch.setenv("GOOGLE_COWORKER_REDIRECT_URI", "http://localhost:5000/api/coworker/connections/google/callback")
    monkeypatch.delenv("GOOGLE_OAUTH_REDIRECT_URI", raising=False)
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "client-id")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "secret")
    started = client.post("/api/coworker/connections/google/start", headers=auth_headers)
    assert started.status_code == 503
    assert started.get_json()["code"] == "not_configured"
