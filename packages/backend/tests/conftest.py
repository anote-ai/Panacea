"""Shared pytest fixtures."""
import os
import sys

import pytest

# Ensure packages/backend is on the path when running from CI
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app  # noqa: E402


@pytest.fixture
def app(tmp_path):
    return create_app({
        "TESTING": True,
        "JWT_SECRET_KEY": "test-secret",
        "DB_HOST": "localhost",
        "ANTHROPIC_API_KEY": "",
        "STRIPE_SECRET_KEY": "",
        "CHAT_SESSION_DB_PATH": str(tmp_path / "chat_sessions.sqlite3"),
        "UPLOAD_FOLDER": str(tmp_path / "uploads"),
        "DOCUMENT_METADATA_DB_PATH": str(tmp_path / "documents.sqlite3"),
    })


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_headers(client, app):
    with app.app_context():
        from flask_jwt_extended import create_access_token
        token = create_access_token(identity="1")
    return {"Authorization": f"Bearer {token}"}
