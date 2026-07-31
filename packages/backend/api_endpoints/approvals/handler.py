"""Remote approvals — the cross-surface handoff primitive.

Lets a running agent session (CLI, bot, scheduled job) pause on a risky action and
have it approved or denied from a *different* surface (Slack, mobile, web) instead
of blocking on someone being at the same terminal. Sessions poll `GET /<id>` until
`status` leaves `pending`; any other surface resolves it via `POST /<id>/respond`.

In-memory store, mirroring the workspaces blueprint's pattern — swap for a real
table (see database/schema.sql) once this needs to survive a backend restart.
"""
from __future__ import annotations

import time
import uuid
from typing import Literal

from flask import Blueprint, jsonify, request

approvals_bp = Blueprint("approvals", __name__, url_prefix="/api/approvals")

Status = Literal["pending", "approved", "denied"]

_approvals: dict[str, dict] = {}

# Approvals older than this are treated as expired on read, so a stuck session
# fails closed instead of hanging forever on a request nobody will ever see.
DEFAULT_TTL_SECONDS = 15 * 60


def _expire_if_stale(approval: dict) -> dict:
    if approval["status"] == "pending" and (time.time() - approval["created_at"]) > approval["ttl_seconds"]:
        approval["status"] = "expired"
        approval["resolved_at"] = time.time()
    return approval


@approvals_bp.get("")
def list_approvals() -> tuple:
    status_filter = request.args.get("status")
    session_filter = request.args.get("session_id")
    items = [_expire_if_stale(dict(a)) for a in _approvals.values()]
    if status_filter:
        items = [a for a in items if a["status"] == status_filter]
    if session_filter:
        items = [a for a in items if a["session_id"] == session_filter]
    items.sort(key=lambda a: a["created_at"], reverse=True)
    return jsonify({"approvals": items}), 200


@approvals_bp.post("")
def create_approval() -> tuple:
    data = request.get_json(silent=True) or {}
    session_id = data.get("session_id", "").strip()
    action = data.get("action", "").strip()
    if not session_id or not action:
        return jsonify({"error": "session_id and action are required"}), 400

    approval_id = str(uuid.uuid4())
    ttl_seconds = data.get("ttl_seconds")
    if ttl_seconds is None:
        ttl_seconds = DEFAULT_TTL_SECONDS
    _approvals[approval_id] = {
        "id": approval_id,
        "session_id": session_id,
        "action": action,
        "detail": data.get("detail", ""),
        "status": "pending",
        "created_at": time.time(),
        "resolved_at": None,
        "responder": None,
        "ttl_seconds": ttl_seconds,
    }
    return jsonify(_approvals[approval_id]), 201


@approvals_bp.get("/<approval_id>")
def get_approval(approval_id: str) -> tuple:
    approval = _approvals.get(approval_id)
    if not approval:
        return jsonify({"error": "Approval not found"}), 404
    return jsonify(_expire_if_stale(approval)), 200


@approvals_bp.post("/<approval_id>/respond")
def respond_approval(approval_id: str) -> tuple:
    approval = _approvals.get(approval_id)
    if not approval:
        return jsonify({"error": "Approval not found"}), 404
    approval = _expire_if_stale(approval)
    if approval["status"] != "pending":
        return jsonify({"error": f"Approval already {approval['status']}"}), 409

    data = request.get_json(silent=True) or {}
    if "approved" not in data:
        return jsonify({"error": "approved (boolean) is required"}), 400

    approval["status"] = "approved" if data["approved"] else "denied"
    approval["resolved_at"] = time.time()
    approval["responder"] = data.get("responder", "unknown")
    return jsonify(approval), 200
