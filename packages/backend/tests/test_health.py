"""Tests for health endpoints."""


def test_health(client, monkeypatch):
    monkeypatch.setenv("PANACEA_BUILD_SHA", "abc123")
    monkeypatch.setenv("PANACEA_VERSION", "1.2.3")

    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "ok"
    assert data["service"] == "anote-backend"
    assert data["version"] == "1.2.3"
    assert data["commit"] == "abc123"


def test_version_uses_safe_fallbacks(client, monkeypatch):
    for name in ("PANACEA_BUILD_SHA", "GITHUB_SHA", "COMMIT_SHA", "SOURCE_VERSION"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.delenv("PANACEA_VERSION", raising=False)

    resp = client.get("/api/version")
    assert resp.status_code == 200
    assert resp.get_json() == {
        "service": "anote-backend",
        "version": "1.0.0",
        "commit": "unknown",
    }
    assert client.get("/version").get_json() == resp.get_json()


def test_version_accepts_common_ci_sha(client, monkeypatch):
    monkeypatch.delenv("PANACEA_BUILD_SHA", raising=False)
    monkeypatch.setenv("GITHUB_SHA", "github-sha")

    resp = client.get("/api/version")
    assert resp.status_code == 200
    assert resp.get_json()["commit"] == "github-sha"


def test_root(client, monkeypatch):
    monkeypatch.setenv("PANACEA_BUILD_SHA", "root-sha")

    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["name"] == "Anote AI Backend"
    assert data["version"] == "1.0.0"
    assert data["commit"] == "root-sha"
