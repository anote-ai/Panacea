"""Production configuration checks.

When ``APP_ENV=production`` the app refuses to start with settings that
would make the coworker unsafe: a default or short JWT secret, OAuth
tokens encrypted with a key derived from the JWT secret, or the coworker
store on SQLite. Missing public URLs are reported as warnings.

Set ``ALLOW_UNSAFE_CONFIG=1`` only to get a broken deploy running again
while you fix the configuration.

Check an environment before deploying, so a bad setting fails the check
instead of taking the running app down::

    APP_ENV=production python -m coworker.config      # exits 1 on errors
"""
from __future__ import annotations

import logging
import os
from collections.abc import Mapping
from typing import Any
from urllib.parse import urlsplit

log = logging.getLogger("coworker.config")

DEFAULT_SECRETS = {"", "dev-secret-change-me", "change-me-in-production", "test-secret"}


def check(env: Mapping[str, Any]) -> tuple[list[str], list[str]]:
    """Return (errors, warnings) for a production environment."""
    errors: list[str] = []
    warnings: list[str] = []
    jwt = str(env.get("JWT_SECRET_KEY") or "")
    if jwt in DEFAULT_SECRETS or len(jwt) < 32:
        errors.append("JWT_SECRET_KEY must be a random value of at least 32 characters.")
    if not env.get("PROVIDER_KEY_ENCRYPTION_KEY"):
        errors.append("PROVIDER_KEY_ENCRYPTION_KEY is required: it encrypts users' OAuth and API keys at rest.")
    else:
        from services.provider_keys import _configured_fernet

        try:
            _configured_fernet(str(env["PROVIDER_KEY_ENCRYPTION_KEY"]))
        except ValueError:
            errors.append("PROVIDER_KEY_ENCRYPTION_KEY must be a Fernet key or a URL-safe random secret of at least 32 bytes.")
    if str(env.get("COWORKER_DB_URL") or "").startswith("sqlite"):
        errors.append("COWORKER_DB_URL must not point at SQLite in production.")
    for key in ("BACKEND_URL", "FRONTEND_URL"):
        value = str(env.get(key) or "")
        if not value.startswith("https://"):
            warnings.append(f"{key} should be the public https:// URL (OAuth redirects and webhooks use it).")
    if env.get("GOOGLE_CLIENT_ID"):
        backend_url = str(env.get("BACKEND_URL") or "http://localhost:5000").rstrip("/")
        override = str(env.get("GOOGLE_COWORKER_REDIRECT_URI") or "")
        if override.startswith("https://"):
            google_redirect = override
        elif backend_url.startswith("https://"):
            google_redirect = f"{backend_url}/api/coworker/connections/google/callback"
        else:
            google_redirect = (str(env.get("GOOGLE_OAUTH_REDIRECT_URI") or "") or
                               f"{backend_url}/api/coworker/connections/google/callback")
        if not google_redirect.startswith("https://"):
            warnings.append("GOOGLE_COWORKER_REDIRECT_URI (or its BACKEND_URL fallback) should be https:// in production.")
        elif urlsplit(google_redirect).netloc != urlsplit(backend_url).netloc:
            warnings.append("Google Coworker callback host differs from BACKEND_URL; check its routing and Google Cloud authorized redirect URI.")
    if env.get("MICROSOFT_CLIENT_ID"):
        backend_url = str(env.get("BACKEND_URL") or "http://localhost:5000").rstrip("/")
        for key, path in (("MICROSOFT_REDIRECT_URI", "/api/coworker/connections/microsoft/callback"),
                          ("MICROSOFT_LOGIN_REDIRECT_URI", "/auth/microsoft/callback")):
            redirect = str(env.get(key) or f"{backend_url}{path}")
            if not redirect.startswith("https://"):
                warnings.append(f"{key} (or its BACKEND_URL fallback) should be https:// in production.")
    if env.get("GMAIL_PUSH_AUDIENCE") and not env.get("GMAIL_PUSH_SERVICE_ACCOUNT"):
        errors.append("GMAIL_PUSH_AUDIENCE needs GMAIL_PUSH_SERVICE_ACCOUNT: any Google account can mint a token for an audience.")
    if env.get("SLACK_CLIENT_ID") and not env.get("SLACK_SIGNING_SECRET"):
        warnings.append("SLACK_SIGNING_SECRET is unset: Slack is polled every minute instead of answered in real time.")
    if not env.get("TWIN_S3_BUCKET"):
        warnings.append("TWIN_S3_BUCKET is unset: twin files and consent evidence will be stored on container disk.")
    if not any(env.get(key) for key in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY")):
        warnings.append("No hosted-model API key is set: the coworker uses the local model at OLLAMA_BASE_URL if it "
                        "answers, otherwise its offline planner.")
    return errors, warnings


def enforce(env: Mapping[str, Any] | None = None) -> None:
    env = env if env is not None else os.environ
    if str(env.get("APP_ENV") or "") != "production":
        return
    errors, warnings = check(env)
    for w in warnings:
        log.warning("config: %s", w)
    if errors:
        message = "Unsafe production configuration:\n- " + "\n- ".join(errors)
        if env.get("ALLOW_UNSAFE_CONFIG") == "1":
            log.critical("%s\n(ALLOW_UNSAFE_CONFIG=1 set; starting anyway)", message)
            return
        raise RuntimeError(message)


def main() -> int:  # pragma: no cover - CLI wrapper
    errors, warnings = check(os.environ)
    for w in warnings:
        print(f"warning: {w}")
    for e in errors:
        print(f"ERROR: {e}")
    print("OK: safe to start in production" if not errors else "Fix the errors above before deploying.")
    return 1 if errors else 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
