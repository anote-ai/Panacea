"""Tests for health endpoints."""

from unittest.mock import Mock

import requests


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "ok"
    assert data["service"] == "anote-backend"
    assert data["readiness"] in ("ready", "degraded")
    assert "checks" in data
    assert "providers" in data
    assert "warnings" in data


def test_health_reports_partial_google_config(client, monkeypatch):
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "google-client-id")
    monkeypatch.delenv("GOOGLE_CLIENT_SECRET", raising=False)

    resp = client.get("/health")
    data = resp.get_json()

    assert resp.status_code == 200
    assert data["checks"]["googleAuthConfigured"] is False
    assert "google_auth_partial_config" in data["warnings"]


def test_health_reports_ollama_as_available_when_reachable(client, monkeypatch):
    monkeypatch.setattr("app.requests.get", Mock(return_value=Mock(ok=True)))

    resp = client.get("/health")
    data = resp.get_json()

    assert resp.status_code == 200
    assert data["providers"]["ollama"] is True


def test_health_reports_ollama_as_unavailable_when_unreachable(client, monkeypatch):
    monkeypatch.setattr("app.requests.get", Mock(side_effect=requests.RequestException("connection refused")))

    resp = client.get("/health")
    data = resp.get_json()

    assert resp.status_code == 200
    assert data["providers"]["ollama"] is False


def test_root(client):
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "name" in data
    assert "version" in data
