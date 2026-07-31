"""Tests for the remote-approvals API — the cross-surface handoff primitive."""
from __future__ import annotations

import pytest

from api_endpoints.approvals import handler as approvals_handler


@pytest.fixture(autouse=True)
def clean_store(monkeypatch):
    monkeypatch.setattr(approvals_handler, "_approvals", {})


def test_list_empty(client):
    resp = client.get("/api/approvals")
    assert resp.status_code == 200
    assert resp.get_json() == {"approvals": []}


def test_create_requires_session_and_action(client):
    resp = client.post("/api/approvals", json={"session_id": "s1"})
    assert resp.status_code == 400
    resp = client.post("/api/approvals", json={"action": "rm -rf build/"})
    assert resp.status_code == 400


def test_create_and_get(client):
    resp = client.post("/api/approvals", json={"session_id": "s1", "action": "rm -rf build/"})
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["status"] == "pending"
    assert body["session_id"] == "s1"

    fetched = client.get(f"/api/approvals/{body['id']}").get_json()
    assert fetched["id"] == body["id"]
    assert fetched["status"] == "pending"


def test_get_not_found(client):
    resp = client.get("/api/approvals/does-not-exist")
    assert resp.status_code == 404


def test_list_filters_by_session_and_status(client):
    a1 = client.post("/api/approvals", json={"session_id": "s1", "action": "deploy"}).get_json()
    client.post("/api/approvals", json={"session_id": "s2", "action": "deploy"})
    client.post(f"/api/approvals/{a1['id']}/respond", json={"approved": True})

    by_session = client.get("/api/approvals?session_id=s1").get_json()["approvals"]
    assert len(by_session) == 1
    assert by_session[0]["session_id"] == "s1"

    pending = client.get("/api/approvals?status=pending").get_json()["approvals"]
    assert len(pending) == 1
    assert pending[0]["session_id"] == "s2"


def test_respond_approve(client):
    created = client.post("/api/approvals", json={"session_id": "s1", "action": "deploy"}).get_json()
    resp = client.post(f"/api/approvals/{created['id']}/respond", json={"approved": True, "responder": "slack:alice"})
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["status"] == "approved"
    assert body["responder"] == "slack:alice"
    assert body["resolved_at"] is not None


def test_respond_deny(client):
    created = client.post("/api/approvals", json={"session_id": "s1", "action": "deploy"}).get_json()
    resp = client.post(f"/api/approvals/{created['id']}/respond", json={"approved": False})
    assert resp.get_json()["status"] == "denied"


def test_respond_requires_approved_field(client):
    created = client.post("/api/approvals", json={"session_id": "s1", "action": "deploy"}).get_json()
    resp = client.post(f"/api/approvals/{created['id']}/respond", json={})
    assert resp.status_code == 400


def test_respond_not_found(client):
    resp = client.post("/api/approvals/does-not-exist/respond", json={"approved": True})
    assert resp.status_code == 404


def test_respond_twice_conflicts(client):
    created = client.post("/api/approvals", json={"session_id": "s1", "action": "deploy"}).get_json()
    client.post(f"/api/approvals/{created['id']}/respond", json={"approved": True})
    resp = client.post(f"/api/approvals/{created['id']}/respond", json={"approved": False})
    assert resp.status_code == 409


def test_expires_after_ttl(client, monkeypatch):
    created = client.post(
        "/api/approvals", json={"session_id": "s1", "action": "deploy", "ttl_seconds": 0}
    ).get_json()
    fetched = client.get(f"/api/approvals/{created['id']}").get_json()
    assert fetched["status"] == "expired"


def test_expired_cannot_be_resolved(client):
    created = client.post(
        "/api/approvals", json={"session_id": "s1", "action": "deploy", "ttl_seconds": 0}
    ).get_json()
    resp = client.post(f"/api/approvals/{created['id']}/respond", json={"approved": True})
    assert resp.status_code == 409
