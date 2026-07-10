"""Origin-verification for CloudFront-fronted deployments (PR #257 step 4).

The Panacea EC2 backend port must stay open to 0.0.0.0/0 because CloudFront
has no fixed IP range; the only thing stopping direct hits is a shared
secret CloudFront attaches to every forwarded request as the
X-Panacea-Origin-Verify header. This middleware enforces it.

Disabled when PANACEA_ORIGIN_VERIFY is unset (local dev, CI, docker-compose
dev stack are unaffected). /health stays open so instance-local health
checks work without the secret.
"""
from __future__ import annotations

import hmac

from flask import Flask, jsonify, request

ORIGIN_VERIFY_HEADER = "X-Panacea-Origin-Verify"

_EXEMPT_PATHS = {"/health"}


def init_origin_verify(app: Flask) -> None:
    """Reject requests missing the origin-verify secret, when configured."""
    secret = app.config.get("PANACEA_ORIGIN_VERIFY") or ""
    if not secret:
        return

    @app.before_request
    def _verify_origin():  # type: ignore[no-untyped-def]
        if request.path in _EXEMPT_PATHS:
            return None
        provided = request.headers.get(ORIGIN_VERIFY_HEADER, "")
        if not hmac.compare_digest(provided, secret):
            return jsonify({"error": "Forbidden"}), 403
        return None
