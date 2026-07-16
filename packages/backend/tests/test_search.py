"""Tests for search, user, and misc endpoints."""
import io
import json
from unittest.mock import MagicMock, patch


def _mock_cnx(fetchall=None, fetchone=None, lastrowid=1, rowcount=1):
    cursor = MagicMock()
    cursor.fetchall.return_value = fetchall if fetchall is not None else []
    cursor.fetchone.return_value = fetchone
    cursor.lastrowid = lastrowid
    cursor.rowcount = rowcount
    cnx = MagicMock()
    cnx.cursor.return_value = cursor
    return cnx


def test_search_missing_query(client):
    resp = client.get("/api/search")
    assert resp.status_code == 400


def test_search_no_index(client, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    resp = client.get(f"/api/search?q=test&cwd={tmp_path}")
    assert resp.status_code == 404


def test_search_with_index(client, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    idx_dir = tmp_path / ".anote" / "index"
    idx_dir.mkdir(parents=True)
    chunks = [
        {"file": "src/auth.ts", "startLine": 1, "endLine": 20, "content": "JWT authentication middleware"},
        {"file": "src/db.ts", "startLine": 1, "endLine": 30, "content": "MySQL database connection pool"},
    ]
    (idx_dir / "chunks.json").write_text(json.dumps(chunks))
    resp = client.get(f"/api/search?q=authentication&cwd={tmp_path}&top=5")
    assert resp.status_code == 200
    assert "results" in resp.get_json()


def test_user_profile(client, auth_headers):
    user = {"id": 1, "name": "Jane Doe", "email": "jane@example.com"}
    with patch("api_endpoints.user.handler.get_connection", return_value=_mock_cnx(fetchone=user)):
        resp = client.get("/api/user/profile", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["userId"] == 1
    assert body["name"] == "Jane Doe"
    assert body["email"] == "jane@example.com"
    assert body["hasAvatar"] is False


def test_user_profile_no_auth(client):
    resp = client.get("/api/user/profile")
    assert resp.status_code == 401


def test_user_profile_not_found(client, auth_headers):
    with patch("api_endpoints.user.handler.get_connection", return_value=_mock_cnx(fetchone=None)):
        resp = client.get("/api/user/profile", headers=auth_headers)
    assert resp.status_code == 404


def test_user_update_profile(client, auth_headers):
    with patch("api_endpoints.user.handler.get_connection", return_value=_mock_cnx()):
        resp = client.put("/api/user/profile", json={"name": "New Name"}, headers=auth_headers)
    assert resp.status_code == 200


def test_user_update_profile_no_name(client, auth_headers):
    resp = client.put("/api/user/profile", json={}, headers=auth_headers)
    assert resp.status_code == 200


def test_user_update_profile_empty_name(client, auth_headers):
    resp = client.put("/api/user/profile", json={"name": "   "}, headers=auth_headers)
    assert resp.status_code == 400


def test_user_update_profile_no_auth(client):
    resp = client.put("/api/user/profile", json={"name": "New Name"})
    assert resp.status_code == 401


def test_upload_avatar_no_auth(client):
    resp = client.post("/api/user/avatar")
    assert resp.status_code == 401


def test_upload_avatar_no_file(client, auth_headers):
    resp = client.post("/api/user/avatar", headers=auth_headers)
    assert resp.status_code == 400


def test_upload_avatar_bad_type(client, auth_headers):
    data = {"file": (io.BytesIO(b"not an image"), "avatar.gif", "image/gif")}
    resp = client.post(
        "/api/user/avatar", data=data,
        content_type="multipart/form-data", headers=auth_headers,
    )
    assert resp.status_code == 400


def test_upload_avatar_too_large(client, auth_headers):
    big = io.BytesIO(b"x" * (5 * 1024 * 1024 + 1))
    data = {"file": (big, "avatar.png", "image/png")}
    resp = client.post(
        "/api/user/avatar", data=data,
        content_type="multipart/form-data", headers=auth_headers,
    )
    assert resp.status_code == 400


def test_upload_avatar_success(client, auth_headers, tmp_path):
    from PIL import Image

    buf = io.BytesIO()
    Image.new("RGB", (400, 400), "blue").save(buf, format="PNG")
    buf.seek(0)

    with patch("services.avatars.AVATAR_FOLDER", tmp_path):
        data = {"file": (buf, "avatar.png", "image/png")}
        resp = client.post(
            "/api/user/avatar", data=data,
            content_type="multipart/form-data", headers=auth_headers,
        )
    assert resp.status_code == 200
    assert (tmp_path / "1.png").exists()


def test_get_avatar_no_auth(client):
    resp = client.get("/api/user/avatar")
    assert resp.status_code == 401


def test_get_avatar_not_found(client, auth_headers, tmp_path):
    with patch("api_endpoints.user.handler.avatar_path", return_value=tmp_path / "missing.png"):
        resp = client.get("/api/user/avatar", headers=auth_headers)
    assert resp.status_code == 404


def test_get_avatar_success(client, auth_headers, tmp_path):
    avatar_file = tmp_path / "1.png"
    avatar_file.write_bytes(b"\x89PNG\r\n\x1a\nfakepngdata")
    with patch("api_endpoints.user.handler.avatar_path", return_value=avatar_file):
        resp = client.get("/api/user/avatar", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.mimetype == "image/png"


def test_delete_avatar_no_auth(client):
    resp = client.delete("/api/user/avatar")
    assert resp.status_code == 401


def test_delete_avatar(client, auth_headers, tmp_path):
    avatar_file = tmp_path / "1.png"
    avatar_file.write_bytes(b"fake")
    with patch("services.avatars.AVATAR_FOLDER", tmp_path):
        resp = client.delete("/api/user/avatar", headers=auth_headers)
    assert resp.status_code == 200
    assert not avatar_file.exists()


def test_api_keys_list(client, auth_headers):
    resp = client.get("/api/user/api-keys", headers=auth_headers)
    assert resp.status_code == 200
    assert "keys" in resp.get_json()


def test_api_keys_create(client, auth_headers):
    resp = client.post("/api/user/api-keys", headers=auth_headers)
    assert resp.status_code == 201
    assert resp.get_json()["key"].startswith("ak-")


def test_api_keys_delete_not_found(client, auth_headers):
    resp = client.delete("/api/user/api-keys/nonexistent-prefix", headers=auth_headers)
    assert resp.status_code == 404


def test_workspaces_non_hosted(client):
    resp = client.get("/api/workspaces")
    assert resp.status_code == 501


def test_payments_no_stripe(client):
    resp = client.post("/api/payments/checkout", json={"priceId": "price_test"})
    assert resp.status_code == 503


def test_payments_portal_no_stripe(client):
    resp = client.post("/api/payments/portal", json={"customerId": "cus_test"})
    assert resp.status_code == 503


def test_rate_limiter():
    from middleware.rate_limit import RateLimiter
    limiter = RateLimiter(max_calls=3, period=60.0)
    assert limiter.is_allowed("user1") is True
    assert limiter.is_allowed("user1") is True
    assert limiter.is_allowed("user1") is True
    assert limiter.is_allowed("user1") is False
    assert limiter.is_allowed("user2") is True


def test_llm_provider_detection():
    from services.llm import get_provider_for_model
    assert get_provider_for_model("claude-sonnet-4-6") == "anthropic"
    assert get_provider_for_model("gpt-4o") == "openai"
    assert get_provider_for_model("gemini-2.0-flash") == "google"
    assert get_provider_for_model("llama3") == "ollama"


def test_search_rejects_mismatched_cwd(client, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    resp = client.get("/api/search?q=test&cwd=/tmp/other-project")
    assert resp.status_code == 400


def test_search_service_no_index(tmp_path, monkeypatch):
    from services.search import has_index, search_index

    monkeypatch.chdir(tmp_path)
    assert has_index() is False
    assert search_index("query") == []


def test_rag_chunk_text():
    from services.rag import _chunk_text
    chunks = _chunk_text("a" * 2500, chunk_size=1000, overlap=100)
    assert len(chunks) > 1


def test_rag_empty_text():
    from services.rag import _chunk_text
    assert _chunk_text("") == []
    assert _chunk_text("   ") == []
