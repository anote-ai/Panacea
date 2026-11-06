"""Auth middleware: a signed-in session (JWT), or a coworker API token on its allowed routes."""
from __future__ import annotations

import functools
from collections.abc import Callable

from flask import g, jsonify, request
from flask_jwt_extended import verify_jwt_in_request

TOKEN_PREFIX = "Bearer ogn_"


def _token_user() -> tuple[int | None, tuple | None]:
    """(user id, None) for a valid API token on an allowed route; (None, error response) otherwise."""
    from coworker import api_tokens
    from coworker.store import get_store

    if not request.path.startswith("/api/coworker/") or not api_tokens.allowed(request.method, request.path):
        return None, (jsonify({"error": "API tokens can't do this. Sign in to the app.", "code": "token_not_allowed"}), 403)
    user_id = api_tokens.verify(get_store(), request.headers.get("Authorization", "")[len("Bearer "):].strip())
    if user_id is None:
        return None, (jsonify({"error": "Unauthorized"}), 401)
    return user_id, None


def require_auth(fn: Callable) -> Callable:
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):  # type: ignore[no-untyped-def]
        if request.headers.get("Authorization", "").startswith(TOKEN_PREFIX):
            user_id, failure = _token_user()
            if failure is not None:
                return failure
            g.coworker_token_user = user_id
            return fn(*args, **kwargs)
        try:
            verify_jwt_in_request()
        except Exception:
            return jsonify({"error": "Unauthorized"}), 401
        return fn(*args, **kwargs)
    return wrapper
