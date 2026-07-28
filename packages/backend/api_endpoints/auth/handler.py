"""Authentication endpoints — register, login, refresh, Google OAuth."""
from __future__ import annotations

import os
import secrets

import bcrypt
from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


@auth_bp.post("/register")
def register() -> tuple:
    """Register a new user."""
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    name = data.get("name") or ""

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400

    try:
        from database.db import create_user, get_connection, get_user_by_email
        cnx = get_connection()
        if get_user_by_email(cnx, email):
            cnx.close()
            return jsonify({"error": "Email already registered"}), 409
        user_id = create_user(cnx, email, _hash_password(password), name)
        cnx.close()
        token = create_access_token(identity=str(user_id))
        return jsonify({"token": token, "userId": user_id}), 201
    except Exception:
        return jsonify({"error": "Authentication service unavailable"}), 503


@auth_bp.post("/login")
def login() -> tuple:
    """Authenticate a user and return a JWT."""
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    try:
        from database.db import get_connection, get_user_by_email
        cnx = get_connection()
        user = get_user_by_email(cnx, email)
        cnx.close()
        if not user or not _check_password(password, user["password_hash"]):
            return jsonify({"error": "Invalid credentials"}), 401
        token = create_access_token(identity=str(user["id"]))
        return jsonify({"token": token, "userId": user["id"]}), 200
    except Exception:
        return jsonify({"error": "Authentication service unavailable"}), 503


@auth_bp.post("/google")
def google_login() -> tuple:
    """Authenticate a user via a Google Identity Services ID token."""
    data = request.get_json(silent=True) or {}
    credential = data.get("credential") or ""
    client_id = os.environ.get("GOOGLE_CLIENT_ID", "")

    if not credential:
        return jsonify({"error": "Missing Google credential"}), 400
    if not client_id:
        return jsonify({"error": "Google sign-in is not configured"}), 503

    try:
        claims = google_id_token.verify_oauth2_token(
            credential, google_requests.Request(), client_id
        )
    except ValueError:
        return jsonify({"error": "Invalid Google credential"}), 401

    email = (claims.get("email") or "").strip().lower()
    if not email or not claims.get("email_verified"):
        return jsonify({"error": "Google account has no verified email"}), 401
    name = claims.get("name") or ""

    try:
        from database.db import create_user, get_connection, get_user_by_email
        cnx = get_connection()
        user = get_user_by_email(cnx, email)
        if not user:
            random_password = _hash_password(secrets.token_urlsafe(32))
            user_id = create_user(cnx, email, random_password, name)
        else:
            user_id = user["id"]
        cnx.close()
        token = create_access_token(identity=str(user_id))
        return jsonify({"token": token, "userId": user_id}), 200
    except Exception:
        return jsonify({"error": "Authentication service unavailable"}), 503


@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh() -> tuple:
    """Refresh a JWT access token."""
    identity = get_jwt_identity()
    token = create_access_token(identity=identity)
    return jsonify({"token": token}), 200


@auth_bp.get("/me")
@jwt_required()
def me() -> tuple:
    """Return the current user's identity."""
    identity = get_jwt_identity()
    return jsonify({"userId": identity}), 200
