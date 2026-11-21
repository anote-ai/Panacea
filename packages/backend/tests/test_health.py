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


def test_health_db_ok(client):
    from unittest.mock import MagicMock, patch

    cnx = MagicMock()
    with patch("database.db.get_connection", return_value=cnx):
        resp = client.get("/health/db")
    assert resp.status_code == 200
    assert resp.get_json() == {"database": "ok"}
    executed = cnx.cursor.return_value.execute.call_args.args[0]
    assert "FROM users" in executed
    cnx.close.assert_called_once()


def test_health_db_reports_errno_without_details(client):
    from unittest.mock import patch

    from mysql.connector.errors import ProgrammingError

    err = ProgrammingError(msg="Table 'anote.users' doesn't exist", errno=1146)
    with patch("database.db.get_connection", side_effect=err):
        resp = client.get("/health/db")
    assert resp.status_code == 503
    data = resp.get_json()
    assert data == {"database": "unavailable", "error": "ProgrammingError", "errno": 1146}
    # Connection details / raw messages must not leak to the public endpoint.
    assert "anote.users" not in resp.get_data(as_text=True)


def test_health_stays_ok_when_database_is_down(client):
    from unittest.mock import patch

    with patch("database.db.get_connection", side_effect=RuntimeError("down")):
        assert client.get("/health").status_code == 200
        assert client.get("/health/db").status_code == 503
