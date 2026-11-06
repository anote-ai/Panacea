"""Personal access tokens for the SDK, the CLI and scripts.

A token (``ogn_`` + 40 random characters) is shown once and stored only as a
SHA-256 hash. It works on an allowlist of coworker routes: handing work to the
AI engineer, code reviews, the scorecard, reading the knowledge pack, and
reading actions and the trial. Approving, sending, billing, connections,
data deletion and token management always need a signed-in browser session,
so a leaked token can't push code, send email or spend money.
"""
from __future__ import annotations

import hashlib
import re
import secrets
from typing import Any

from coworker.store import Store, iso

PREFIX = "ogn_"
MAX_TOKENS = 20

# (method, path under /api/coworker) a token may call.
ALLOWED: list[tuple[str, re.Pattern[str]]] = [
    (m, re.compile(p)) for m, p in [
        ("GET", r"^/engineer/runs(/\d+)?$"),
        ("POST", r"^/engineer/runs$"),
        ("PATCH", r"^/engineer/runs/\d+/(spec|graph)$"),
        ("POST", r"^/engineer/runs/\d+/(plan|start)$"),
        ("GET", r"^/reviews(/\d+)?$"),
        ("POST", r"^/reviews$"),
        ("GET", r"^/scorecard$"),
        ("GET", r"^/knowledge-pack$"),
        ("GET", r"^/actions$"),
        ("GET", r"^/trial$"),
    ]
]


def _hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def allowed(method: str, path: str) -> bool:
    sub = path.removeprefix("/api/coworker")
    return any(m == method and p.match(sub) for m, p in ALLOWED)


def create(store: Store, user_id: int, name: str) -> tuple[dict[str, Any], str]:
    name = name.strip()[:80] or "Token"
    active = store.one("SELECT COUNT(*) AS n FROM cw_api_tokens WHERE user_id = %s AND revoked_at IS NULL", (user_id,))
    if int((active or {}).get("n") or 0) >= MAX_TOKENS:
        raise ValueError(f"You can have up to {MAX_TOKENS} tokens. Revoke one first.")
    token = PREFIX + secrets.token_urlsafe(30)
    token_id = store.insert("cw_api_tokens", {"user_id": user_id, "name": name, "token_hash": _hash(token),
                                              "prefix": token[:8], "created_at": iso()})
    store.log(user_id, "security", f"Created API token “{name}”")
    row = store.get("cw_api_tokens", token_id, user_id)
    assert row is not None
    return row, token


def verify(store: Store, token: str) -> int | None:
    if not token.startswith(PREFIX):
        return None
    row = store.one("SELECT id, user_id FROM cw_api_tokens WHERE token_hash = %s AND revoked_at IS NULL", (_hash(token),))
    if not row:
        return None
    store.update("cw_api_tokens", row["id"], None, {"last_used_at": iso()})
    return int(row["user_id"])


def revoke(store: Store, user_id: int, token_id: int) -> bool:
    row = store.get("cw_api_tokens", token_id, user_id)
    if not row or row.get("revoked_at"):
        return False
    store.update("cw_api_tokens", token_id, user_id, {"revoked_at": iso()})
    store.log(user_id, "security", f"Revoked API token “{row['name']}”")
    return True


def listing(store: Store, user_id: int) -> list[dict[str, Any]]:
    rows = store.query("SELECT id, name, prefix, created_at, last_used_at FROM cw_api_tokens WHERE user_id = %s "
                       "AND revoked_at IS NULL ORDER BY id DESC", (user_id,))
    return [{"id": r["id"], "name": r["name"], "prefix": r["prefix"], "createdAt": r["created_at"],
             "lastUsedAt": r.get("last_used_at")} for r in rows]
