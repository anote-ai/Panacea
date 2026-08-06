"""Anote AI unified backend — Flask application factory."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

from api_endpoints.auth.handler import auth_bp, google_oauth_callback
from api_endpoints.chat.handler import chat_bp
from api_endpoints.documents.handler import documents_bp
from api_endpoints.folders.handler import folders_bp
from api_endpoints.payments.handler import payments_bp
from api_endpoints.search.handler import search_bp
from api_endpoints.user.handler import user_bp
from api_endpoints.workspaces.handler import workspaces_bp

load_dotenv(Path(__file__).resolve().with_name(".env"))


def _config_string(app: Flask, key: str, default: str = "") -> str:
    value = os.environ.get(key)
    if value is None:
        value = app.config.get(key, default)
    return str(value or default)


def _build_health_report(app: Flask) -> dict[str, Any]:
    app_env = os.environ.get("APP_ENV", "local")
    jwt_secret = _config_string(app, "JWT_SECRET_KEY", "dev-secret-change-me")
    provider_key_encryption_key = _config_string(app, "PROVIDER_KEY_ENCRYPTION_KEY")
    google_client_id = _config_string(app, "GOOGLE_CLIENT_ID")
    google_client_secret = _config_string(app, "GOOGLE_CLIENT_SECRET")
    stripe_secret_key = _config_string(app, "STRIPE_SECRET_KEY")
    stripe_webhook_secret = _config_string(app, "STRIPE_WEBHOOK_SECRET")
    stripe_prices = [
        _config_string(app, "STRIPE_PRICE_BASIC"),
        _config_string(app, "STRIPE_PRICE_PRO"),
        _config_string(app, "STRIPE_PRICE_ENTERPRISE"),
    ]
    provider_statuses = {
        "anthropic": bool(_config_string(app, "ANTHROPIC_API_KEY")),
        "openai": bool(_config_string(app, "OPENAI_API_KEY")),
        "google": bool(_config_string(app, "GEMINI_API_KEY")),
        "ollama": bool(_config_string(app, "OLLAMA_BASE_URL")),
    }
    ai_provider_configured = any(
        provider_statuses.values()
    )
    google_auth_configured = bool(google_client_id and google_client_secret)
    billing_configured = bool(
        stripe_secret_key and stripe_webhook_secret and any(price for price in stripe_prices)
    )
    has_partial_google_config = bool(google_client_id) != bool(google_client_secret)
    has_partial_billing_config = bool(
        stripe_secret_key or stripe_webhook_secret or any(price for price in stripe_prices)
    ) and not billing_configured

    warnings: list[str] = []
    if len(jwt_secret) < 32:
        warnings.append("jwt_secret_too_short")
    if app_env != "local" and not provider_key_encryption_key:
        warnings.append("provider_key_encryption_key_missing")
    if has_partial_google_config:
        warnings.append("google_auth_partial_config")
    if has_partial_billing_config:
        warnings.append("billing_partial_config")
    if not ai_provider_configured:
        warnings.append("no_llm_provider_configured")

    return {
        "status": "ok",
        "service": "anote-backend",
        "environment": app_env,
        "readiness": "degraded" if warnings else "ready",
        "checks": {
            "googleAuthConfigured": google_auth_configured,
            "billingConfigured": billing_configured,
            "aiProviderConfigured": ai_provider_configured,
            "providerKeyEncryptionConfigured": bool(provider_key_encryption_key),
            "jwtSecretStrong": len(jwt_secret) >= 32,
        },
        "providers": provider_statuses,
        "warnings": warnings,
    }


def create_app(config: dict | None = None) -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)

    app.config.update(
        SECRET_KEY=os.environ.get("JWT_SECRET_KEY", "dev-secret-change-me"),
        JWT_SECRET_KEY=os.environ.get("JWT_SECRET_KEY", "dev-secret-change-me"),
        JWT_ACCESS_TOKEN_EXPIRES=False,
        TESTING=False,
        DB_HOST=os.environ.get("DB_HOST", "127.0.0.1"),
        DB_NAME=os.environ.get("DB_NAME", "anote"),
        DB_USER=os.environ.get("DB_USER", "anote"),
        DB_PASSWORD=os.environ.get("DB_PASSWORD", "anote"),
        REDIS_URL=os.environ.get("REDIS_URL", "redis://localhost:6379"),
        ANTHROPIC_API_KEY=os.environ.get("ANTHROPIC_API_KEY", ""),
        OPENAI_API_KEY=os.environ.get("OPENAI_API_KEY", ""),
        GEMINI_API_KEY=os.environ.get("GEMINI_API_KEY", ""),
        OLLAMA_BASE_URL=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
        STRIPE_SECRET_KEY=os.environ.get("STRIPE_SECRET_KEY", ""),
        STRIPE_WEBHOOK_SECRET=os.environ.get("STRIPE_WEBHOOK_SECRET", ""),
        STRIPE_PRICE_BASIC=os.environ.get("STRIPE_PRICE_BASIC", ""),
        STRIPE_PRICE_PRO=os.environ.get("STRIPE_PRICE_PRO", ""),
        STRIPE_PRICE_ENTERPRISE=os.environ.get("STRIPE_PRICE_ENTERPRISE", ""),
        PROVIDER_KEY_ENCRYPTION_KEY=os.environ.get("PROVIDER_KEY_ENCRYPTION_KEY", ""),
        GOOGLE_CLIENT_ID=os.environ.get("GOOGLE_CLIENT_ID", ""),
        GOOGLE_CLIENT_SECRET=os.environ.get("GOOGLE_CLIENT_SECRET", ""),
        UPLOAD_FOLDER=os.environ.get("UPLOAD_FOLDER", "/tmp/anote_uploads"),
    )
    if config:
        app.config.update(config)

    CORS(app, resources={r"/*": {"origins": "*"}})
    JWTManager(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(folders_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(workspaces_bp)

    app.add_url_rule("/callback", "google_oauth_callback", google_oauth_callback, methods=["GET"])

    if not app.config.get("TESTING"):
        for warning in _build_health_report(app)["warnings"]:
            app.logger.warning("Startup readiness warning: %s", warning)

    @app.get("/health")
    def health() -> tuple:
        return jsonify(_build_health_report(app)), 200

    @app.get("/")
    def root() -> tuple:
        return jsonify({"name": "Anote AI Backend", "version": "1.0.0"}), 200

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("APP_ENV", "local") == "local"
    app.run(host="0.0.0.0", port=port, debug=debug)
