"""Personal API tokens: create once, hashed at rest, allowlisted routes only, revocable."""
from __future__ import annotations

from unittest.mock import patch

import pytest

from coworker import api_tokens
from coworker.store import Store


@pytest.fixture(autouse=True)
def _env(monkeypatch):
    monkeypatch.setenv("COWORKER_OFFLINE", "1")
    with patch("api_endpoints.coworker.common.owner_profile", return_value=("Natan Vidra", "natan@example.com")), \
         patch("api_endpoints.coworker.core.owner_profile", return_value=("Natan Vidra", "natan@example.com")):
        yield


def test_create_verify_revoke(tmp_path):
    s = Store(f"sqlite:///{tmp_path}/t.db")
    row, token = api_tokens.create(s, 1, "  CI  ")
    assert token.startswith("ogn_") and len(token) > 40 and row["name"] == "CI" and row["prefix"] == token[:8]
    assert token not in str(s.query("SELECT * FROM cw_api_tokens"))  # only the hash is stored
    assert api_tokens.verify(s, token) == 1 and api_tokens.listing(s, 1)[0]["lastUsedAt"]
    assert api_tokens.verify(s, "ogn_wrong") is None and api_tokens.verify(s, "eyJjwt") is None
    assert api_tokens.revoke(s, 1, row["id"]) and not api_tokens.revoke(s, 1, row["id"])
    assert api_tokens.verify(s, token) is None and api_tokens.listing(s, 1) == []
    assert not api_tokens.revoke(s, 2, row["id"])


def test_token_limit(tmp_path):
    s = Store(f"sqlite:///{tmp_path}/t.db")
    for i in range(api_tokens.MAX_TOKENS):
        api_tokens.create(s, 1, f"t{i}")
    with pytest.raises(ValueError):
        api_tokens.create(s, 1, "one too many")


def test_allowlist():
    assert api_tokens.allowed("POST", "/api/coworker/engineer/runs")
    assert api_tokens.allowed("POST", "/api/coworker/engineer/runs/4/start")
    assert api_tokens.allowed("GET", "/api/coworker/scorecard")
    for method, path in [("POST", "/api/coworker/actions/1/approve"), ("POST", "/api/coworker/tokens"),
                         ("DELETE", "/api/coworker/data"), ("POST", "/api/coworker/billing/checkout"),
                         ("PATCH", "/api/coworker/knowledge-pack"), ("POST", "/api/coworker/connections/github/token")]:
        assert not api_tokens.allowed(method, path), path


def test_routes_end_to_end(client, auth_headers):
    h = auth_headers
    client.post("/api/coworker", json={"mode": "demo"}, headers=h)
    created = client.post("/api/coworker/tokens", json={"name": "laptop"}, headers=h)
    assert created.status_code == 201
    token = created.get_json()["token"]
    listed = client.get("/api/coworker/tokens", headers=h).get_json()
    assert listed["tokens"][0]["name"] == "laptop" and any("scorecard" in a for a in listed["allowed"])
    t = {"Authorization": f"Bearer {token}"}

    # allowed: hand off a ticket, run it, read results
    run = client.post("/api/coworker/engineer/runs", json={"source": "jira:ACME-142"}, headers=t).get_json()
    client.post(f"/api/coworker/engineer/runs/{run['id']}/plan", headers=t)
    done = client.post(f"/api/coworker/engineer/runs/{run['id']}/start", headers=t).get_json()
    assert done["status"] == "ready"
    assert client.get("/api/coworker/scorecard", headers=t).status_code == 200
    assert client.post("/api/coworker/reviews", json={"repo": "anote-demo/acme-api", "number": 37}, headers=t).status_code == 201

    # not allowed: approving, managing tokens, anything outside the coworker API
    blocked = client.post(f"/api/coworker/actions/{done['actionId']}/approve", headers=t)
    assert blocked.status_code == 403 and blocked.get_json()["code"] == "token_not_allowed"
    assert client.post("/api/coworker/tokens", json={"name": "x"}, headers=t).status_code == 403
    assert client.get("/api/chat/sessions", headers=t).status_code == 403
    assert client.get("/api/coworker/scorecard", headers={"Authorization": "Bearer ogn_nope"}).status_code == 401

    tid = listed["tokens"][0]["id"]
    assert client.delete(f"/api/coworker/tokens/{tid}", headers=h).status_code == 200
    assert client.delete(f"/api/coworker/tokens/{tid}", headers=h).status_code == 404
    assert client.get("/api/coworker/scorecard", headers=t).status_code == 401  # revoked
    with patch("coworker.api_tokens.create", side_effect=ValueError("limit")):
        assert client.post("/api/coworker/tokens", json={}, headers=h).status_code == 409
