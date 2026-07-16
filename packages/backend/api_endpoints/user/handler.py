"""User profile, avatar, and API key management."""
from __future__ import annotations

import os
import secrets
from typing import Any

from flask import Blueprint, jsonify, request, send_file
from flask_jwt_extended import get_jwt_identity, jwt_required

from database.db import get_connection, get_user_by_id, update_user_name
from services.avatars import avatar_path, delete_avatar, save_avatar

user_bp = Blueprint("user", __name__, url_prefix="/api/user")

_api_keys: dict[str, list[str]] = {}

_ALLOWED_AVATAR_TYPES = {"image/png", "image/jpeg", "image/webp"}
_MAX_AVATAR_SIZE = 5 * 1024 * 1024  # 5MB


@user_bp.get("/profile")
@jwt_required()
def get_profile() -> tuple:
    user_id = int(get_jwt_identity())
    cnx = get_connection()
    try:
        user = get_user_by_id(cnx, user_id)
    finally:
        cnx.close()
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({
        "userId": user_id,
        "name": user.get("name") or "",
        "email": user.get("email") or "",
        "hasAvatar": avatar_path(user_id).exists(),
    }), 200


@user_bp.put("/profile")
@jwt_required()
def update_profile() -> tuple:
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    user_id = int(get_jwt_identity())

    if name is not None:
        name = name.strip()
        if not name:
            return jsonify({"error": "Name cannot be empty"}), 400
        cnx = get_connection()
        try:
            update_user_name(cnx, user_id, name)
        finally:
            cnx.close()

    return jsonify({"userId": user_id, "updated": True}), 200


@user_bp.post("/avatar")
@jwt_required()
def upload_avatar() -> tuple:
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    file = request.files["file"]

    content_type = (file.content_type or "").split(";")[0].strip().lower()
    if content_type not in _ALLOWED_AVATAR_TYPES:
        return jsonify({"error": "Unsupported file type — use PNG, JPEG, or WEBP"}), 400

    file.stream.seek(0, os.SEEK_END)
    size = file.stream.tell()
    file.stream.seek(0)
    if size > _MAX_AVATAR_SIZE:
        return jsonify({"error": "File exceeds 5MB limit"}), 400

    user_id = int(get_jwt_identity())
    try:
        save_avatar(user_id, file.stream)
    except Exception as exc:
        print(f"Avatar save failed: {exc}")
        return jsonify({"error": "Internal server error"}), 500

    return jsonify({"uploaded": True}), 200


@user_bp.get("/avatar")
@jwt_required()
def get_avatar() -> Any:
    user_id = int(get_jwt_identity())
    path = avatar_path(user_id)
    if not path.exists():
        return jsonify({"error": "No avatar"}), 404
    return send_file(path, mimetype="image/png", as_attachment=False)


@user_bp.delete("/avatar")
@jwt_required()
def remove_avatar() -> tuple:
    user_id = int(get_jwt_identity())
    delete_avatar(user_id)
    return jsonify({"deleted": True}), 200


@user_bp.get("/api-keys")
@jwt_required()
def list_api_keys() -> tuple:
    user_id = get_jwt_identity()
    keys = _api_keys.get(user_id, [])
    masked = [f"{k[:8]}...{k[-4:]}" for k in keys]
    return jsonify({"keys": masked}), 200


@user_bp.post("/api-keys")
@jwt_required()
def create_api_key() -> tuple:
    user_id = get_jwt_identity()
    key = f"ak-{secrets.token_urlsafe(32)}"
    _api_keys.setdefault(user_id, []).append(key)
    return jsonify({"key": key}), 201


@user_bp.delete("/api-keys/<key_prefix>")
@jwt_required()
def delete_api_key(key_prefix: str) -> tuple:
    user_id = get_jwt_identity()
    keys = _api_keys.get(user_id, [])
    original_len = len(keys)
    _api_keys[user_id] = [k for k in keys if not k.startswith(key_prefix)]
    deleted = original_len - len(_api_keys.get(user_id, []))
    if not deleted:
        return jsonify({"error": "Key not found"}), 404
    return jsonify({"deleted": deleted}), 200
