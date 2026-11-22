"""Anote AI unified backend — Flask application factory."""
from __future__ import annotations

import os

from flask import Flask, Response, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from api_endpoints.auth.handler import auth_bp, google_oauth_callback
from api_endpoints.chat.handler import chat_bp
from api_endpoints.company_demos import demo_bp
from api_endpoints.documents.handler import documents_bp
from api_endpoints.folders.handler import folders_bp
from api_endpoints.payments.handler import payments_bp
from api_endpoints.search.handler import search_bp
from api_endpoints.user.handler import user_bp
from api_endpoints.workspaces.handler import workspaces_bp
from build_metadata import get_build_metadata


def create_app(config: dict[str, object] | None = None) -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)

    app.config.update(
        SECRET_KEY=os.environ.get("JWT_SECRET_KEY", "dev-secret-change-me"),
        JWT_SECRET_KEY=os.environ.get("JWT_SECRET_KEY", "dev-secret-change-me"),
        JWT_ACCESS_TOKEN_EXPIRES=False,
        TESTING=False,
        DB_HOST=os.environ.get("DB_HOST", "localhost"),
        DB_NAME=os.environ.get("DB_NAME", "anote"),
        DB_USER=os.environ.get("DB_USER", "root"),
        DB_PASSWORD=os.environ.get("DB_PASSWORD", ""),
        REDIS_URL=os.environ.get("REDIS_URL", "redis://localhost:6379"),
        ANTHROPIC_API_KEY=os.environ.get("ANTHROPIC_API_KEY", ""),
        OPENAI_API_KEY=os.environ.get("OPENAI_API_KEY", ""),
        GEMINI_API_KEY=os.environ.get("GEMINI_API_KEY", ""),
        STRIPE_SECRET_KEY=os.environ.get("STRIPE_SECRET_KEY", ""),
        UPLOAD_FOLDER=os.environ.get("UPLOAD_FOLDER", "/tmp/anote_uploads"),
    )
    if config:
        app.config.update(config)

    CORS(app, resources={r"/*": {"origins": "*"}})
    JWTManager(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(demo_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(folders_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(workspaces_bp)

    app.add_url_rule("/callback", "google_oauth_callback", google_oauth_callback, methods=["GET"])

    @app.get("/health")
    def health() -> tuple[Response, int]:
        return jsonify({"status": "ok", **get_build_metadata()}), 200

    @app.get("/health/db")
    def health_db() -> tuple[Response, int]:
        """Readiness of the database: reachable, and the users table exists.

        /health stays a pure liveness check (the load balancer uses it), so
        a database outage doesn't pull the API out of rotation. This endpoint
        is what deploys and release checks use to catch a broken database.
        Only the error class and MySQL errno are returned (e.g. 2003 = can't
        connect, 1045 = access denied, 1049 = unknown database, 1146 = table
        missing); the full error goes to the logs.
        """
        try:
            from database.db import get_connection

            cnx = get_connection()
            try:
                cursor = cnx.cursor()
                cursor.execute("SELECT 1 FROM users LIMIT 1")
                cursor.fetchall()
                cursor.close()
            finally:
                cnx.close()
        except Exception as exc:
            app.logger.exception("Database health check failed")
            return jsonify({
                "database": "unavailable",
                "error": type(exc).__name__,
                "errno": getattr(exc, "errno", None),
            }), 503
        return jsonify({"database": "ok"}), 200

    @app.get("/version")
    @app.get("/api/version")
    def version() -> tuple[Response, int]:
        return jsonify(get_build_metadata()), 200

    @app.get("/")
    def root() -> tuple[Response, int]:
        return jsonify({"name": "Anote AI Backend", **get_build_metadata()}), 200

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("APP_ENV", "local") == "local"
    app.run(host="0.0.0.0", port=port, debug=debug)
