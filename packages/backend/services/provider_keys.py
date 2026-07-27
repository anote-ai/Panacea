"""Encryption for user-supplied LLM provider API keys (BYOK)."""
from __future__ import annotations

import base64
import hashlib
import os

from cryptography.fernet import Fernet, InvalidToken

PROVIDERS = ("anthropic", "openai", "google")


def _fernet() -> Fernet:
    key = os.environ.get("PROVIDER_KEY_ENCRYPTION_KEY", "")
    if not key:
        # Derive a stable key from JWT_SECRET_KEY so local/dev setups don't
        # need a second secret configured — production should set its own.
        secret = os.environ.get("JWT_SECRET_KEY", "change-me-in-production")
        key = base64.urlsafe_b64encode(hashlib.sha256(secret.encode()).digest()).decode()
    return Fernet(key.encode())


def encrypt_key(plaintext: str) -> str:
    return _fernet().encrypt(plaintext.encode()).decode()


def decrypt_key(ciphertext: str) -> str:
    return _fernet().decrypt(ciphertext.encode()).decode()


def mask_key(plaintext: str) -> str:
    if len(plaintext) <= 8:
        return "*" * len(plaintext)
    return f"{plaintext[:4]}...{plaintext[-4:]}"


def get_user_provider_key(user_id: int, provider: str) -> str | None:
    """Look up and decrypt a user's own key for `provider`, or None if unset.

    Any DB error here (e.g. the database is unreachable) falls back to None
    rather than propagating — a user-supplied key is an optional override,
    and its absence should never break the server's own configured key.
    """
    from database.db import get_connection, get_provider_key

    try:
        cnx = get_connection()
        try:
            encrypted = get_provider_key(cnx, user_id, provider)
        finally:
            cnx.close()
    except Exception:
        return None
    if not encrypted:
        return None
    try:
        return decrypt_key(encrypted)
    except InvalidToken:
        return None
