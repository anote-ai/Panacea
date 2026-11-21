from __future__ import annotations

import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from scripts.release_smoke import run_checks


class _Handler(BaseHTTPRequestHandler):
    routes: dict[str, tuple[int, str, bytes]] = {}

    def do_GET(self) -> None:  # noqa: N802
        status, content_type, body = self.routes.get(
            self.path,
            (404, "application/json", b'{"error":"not found"}'),
        )
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length") or 0)
        self.rfile.read(length)
        status, content_type, body = self.routes.get(
            "POST " + self.path,
            (404, "application/json", b'{"error":"not found"}'),
        )
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        return


def _json(payload: object) -> bytes:
    return json.dumps(payload).encode()


class ReleaseSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        _Handler.routes = {
            "/": (200, "text/html", b"<title>Ourogen | Chat</title>"),
            "/build.json": (
                200,
                "application/json",
                _json({"service": "panacea-web", "version": "1.0.0", "commit": "abc123"}),
            ),
            "/health": (
                200,
                "application/json",
                _json({"status": "ok", "service": "anote-backend"}),
            ),
            "/api/version": (
                200,
                "application/json",
                _json({"service": "anote-backend", "version": "1.0.0", "commit": "abc123"}),
            ),
            "/health/db": (200, "application/json", _json({"database": "ok"})),
            "POST /auth/login": (401, "application/json", _json({"error": "Invalid credentials"})),
            "/auth/me": (401, "application/json", _json({"msg": "missing token"})),
            "/api/documents": (401, "application/json", _json({"error": "unauthorized"})),
            "/api/user/usage": (401, "application/json", _json({"msg": "missing token"})),
            "/api/payments/plans": (
                200,
                "application/json",
                _json({"plans": [{"plan": "basic", "available": True}]}),
            ),
        }
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def test_all_checks_pass_for_a_matching_release(self) -> None:
        checks = run_checks(
            self.base_url,
            self.base_url,
            expected_sha="abc123",
            require_payments=True,
        )
        self.assertTrue(all(check.ok for check in checks), checks)

    def test_expected_sha_mismatch_is_reported(self) -> None:
        checks = run_checks(self.base_url, self.base_url, expected_sha="different")
        failed = {check.name for check in checks if not check.ok}
        self.assertEqual(
            failed,
            {"frontend-expected-commit", "api-expected-commit"},
        )

    def test_payment_configuration_can_be_required(self) -> None:
        original = _Handler.routes["/api/payments/plans"]
        _Handler.routes["/api/payments/plans"] = (
            200,
            "application/json",
            _json({"plans": [{"plan": "basic", "available": False}]}),
        )
        try:
            checks = run_checks(
                self.base_url,
                self.base_url,
                require_payments=True,
            )
        finally:
            _Handler.routes["/api/payments/plans"] = original
        billing = next(check for check in checks if check.name == "billing-plans")
        self.assertFalse(billing.ok)
        self.assertIn("No paid plan", billing.detail)

    def test_spa_html_cannot_masquerade_as_api_health(self) -> None:
        original = _Handler.routes["/health"]
        _Handler.routes["/health"] = (200, "text/html", b"<title>Panacea</title>")
        try:
            checks = run_checks(self.base_url, self.base_url)
        finally:
            _Handler.routes["/health"] = original
        health = next(check for check in checks if check.name == "api-health")
        self.assertFalse(health.ok)
        self.assertIn("expected application/json", health.detail)

    def _with_routes(self, overrides: dict[str, tuple[int, str, bytes]]):
        saved = dict(_Handler.routes)
        _Handler.routes.update(overrides)
        self.addCleanup(lambda: (_Handler.routes.clear(), _Handler.routes.update(saved)))

    def test_broken_database_fails_db_and_login_checks(self) -> None:
        self._with_routes({
            "/health/db": (
                503,
                "application/json",
                _json({"database": "unavailable", "error": "ProgrammingError", "errno": 1146}),
            ),
            "POST /auth/login": (
                503,
                "application/json",
                _json({"error": "Authentication service unavailable"}),
            ),
        })
        checks = {c.name: c for c in run_checks(self.base_url, self.base_url)}
        self.assertFalse(checks["api-database"].ok)
        self.assertFalse(checks["auth-login"].ok)
        self.assertIn("nobody can sign in", checks["auth-login"].detail)
        # Liveness alone still passes — which is exactly why these checks exist.
        self.assertTrue(checks["api-health"].ok)

    def test_healthy_api_passes_db_and_login_checks(self) -> None:
        checks = {c.name: c for c in run_checks(self.base_url, self.base_url)}
        self.assertTrue(checks["api-database"].ok, checks["api-database"].detail)
        self.assertTrue(checks["auth-login"].ok, checks["auth-login"].detail)


if __name__ == "__main__":
    unittest.main()
