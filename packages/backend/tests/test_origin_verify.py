"""Tests for the X-Panacea-Origin-Verify middleware."""
import pytest

from app import create_app
from middleware.origin_verify import ORIGIN_VERIFY_HEADER

SECRET = "test-origin-secret"


@pytest.fixture
def protected_client(tmp_path):
    app = create_app({
        "TESTING": True,
        "JWT_SECRET_KEY": "test-secret",
        "DB_HOST": "localhost",
        "ANTHROPIC_API_KEY": "",
        "STRIPE_SECRET_KEY": "",
        "PANACEA_ORIGIN_VERIFY": SECRET,
    })
    return app.test_client()


def test_disabled_by_default(client):
    # The shared `client` fixture has no PANACEA_ORIGIN_VERIFY configured
    resp = client.get("/api/documents")
    assert resp.status_code == 200


def test_rejects_missing_header(protected_client):
    resp = protected_client.get("/api/documents")
    assert resp.status_code == 403


def test_rejects_wrong_secret(protected_client):
    resp = protected_client.get(
        "/api/documents", headers={ORIGIN_VERIFY_HEADER: "wrong"}
    )
    assert resp.status_code == 403


def test_accepts_correct_secret(protected_client):
    resp = protected_client.get(
        "/api/documents", headers={ORIGIN_VERIFY_HEADER: SECRET}
    )
    assert resp.status_code == 200


def test_health_exempt(protected_client):
    resp = protected_client.get("/health")
    assert resp.status_code == 200


def test_applies_to_auth_routes(protected_client):
    resp = protected_client.post("/auth/login", json={})
    assert resp.status_code == 403
