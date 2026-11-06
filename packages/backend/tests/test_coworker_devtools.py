"""GitHub, Jira, Notion and MCP connectors: clients, sync, routes, approved actions, undo."""
from __future__ import annotations

import base64
import socket
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from coworker import executor
from coworker.connectors import devtools, github, jira, mcp, notion
from coworker.connectors.base import ConnectorError, decrypt_token, encrypt_token
from coworker.store import Store
from tests.conftest import oauth_return


@pytest.fixture(autouse=True)
def _env(monkeypatch):
    monkeypatch.setenv("COWORKER_OFFLINE", "1")
    with patch("api_endpoints.coworker.common.owner_profile", return_value=("Natan Vidra", "natan@example.com")), \
         patch("api_endpoints.coworker.core.owner_profile", return_value=("Natan Vidra", "natan@example.com")):
        yield


@pytest.fixture
def s(tmp_path):
    store = Store(f"sqlite:///{tmp_path}/dev.db")
    store.create_coworker(1, "Natan Vidra", "natan@example.com", mode="demo")
    return store


def _resp(status: int = 200, body: Any = None, headers: dict | None = None, text: str = "") -> MagicMock:
    r = MagicMock()
    r.status_code = status
    r.content = b"" if body is None and not text else b"x"
    r.json.return_value = body if body is not None else {}
    r.headers = headers or {}
    r.text = text
    r.ok = status < 400
    return r


def _connect(store: Store, provider: str, token: dict) -> None:
    store.upsert_connection(1, provider, account_label=provider, token_enc=encrypt_token(token), status="connected")


# -- GitHub ---------------------------------------------------------------------------

def test_github_token_shapes_and_oauth_url(monkeypatch):
    assert github.looks_like_token("ghp_" + "a" * 36) and github.looks_like_token("github_pat_" + "b" * 30)
    assert not github.looks_like_token("pat-na1-xyz") and not github.looks_like_token("ghp_short")
    monkeypatch.setenv("GITHUB_CLIENT_ID", "cid")
    monkeypatch.setenv("GITHUB_CLIENT_SECRET", "sec")
    assert github.is_configured()
    assert "client_id=cid" in github.auth_url("st") and "scope=repo+read%3Auser" in github.auth_url("st")
    with pytest.raises(ConnectorError):
        github._split("not-a-repo")
    assert github._split("https://github.com/acme/api/") == "acme/api"


def test_github_sync_stores_prs_reviews_and_issues(s):
    def fake(method: str, url: str, **kw: Any) -> MagicMock:
        if url.endswith("/user"):
            return _resp(200, {"login": "natan"})
        if url.endswith("/search/issues"):
            q = kw["params"]["q"]
            if q.startswith("author:"):
                return _resp(200, {"items": [{"number": 5, "title": "fix: rounding", "body": "Round to cents",
                                               "repository_url": "https://api.github.com/repos/acme/api",
                                               "user": {"login": "natan"}, "html_url": "https://github.com/acme/api/pull/5",
                                               "pull_request": {"merged_at": "2026-01-01"}, "updated_at": "2026-01-02T00:00:00Z"}]})
            if q.startswith("reviewed-by:"):
                return _resp(200, {"items": [{"number": 6, "title": "feat: refunds",
                                               "repository_url": "https://api.github.com/repos/acme/api"}]})
            return _resp(200, {"items": [{"number": 7, "title": "Bug in invoices", "state": "open", "labels": [{"name": "bug"}],
                                           "repository_url": "https://api.github.com/repos/acme/api", "user": {"login": "x"}}]})
        if url.endswith("/pulls/5/files"):
            return _resp(200, [{"filename": "app/x.py", "status": "modified", "additions": 3, "deletions": 1, "patch": "@@"}])
        if url.endswith("/pulls/6/comments"):
            return _resp(200, [{"id": 99, "user": {"login": "natan"}, "body": "Please add a test", "path": "app/r.py",
                                "html_url": "u", "created_at": "2026-01-03T00:00:00Z"},
                               {"id": 100, "user": {"login": "someone"}, "body": "lgtm"}])
        raise AssertionError(url)

    with patch("coworker.connectors.github.requests.request", side_effect=fake):
        assert github.GitHubClient({"access_token": "t"}).sync(s, 1) == 3
    kinds = {i["kind"]: i for i in s.items(1, provider="github")}
    assert kinds["pull_request"]["meta"]["files"][0]["path"] == "app/x.py" and kinds["pull_request"]["direction"] == "outbound"
    assert kinds["review_comment"]["body"] == "Please add a test"
    assert kinds["issue"]["meta"]["labels"] == ["bug"]


def test_github_errors_and_rate_limit():
    calls = []

    def fake(method: str, url: str, **kw: Any) -> MagicMock:
        calls.append(url)
        if len(calls) == 1:
            return _resp(429, {}, {"Retry-After": "0"})
        return _resp(401, {"message": "Bad credentials"})

    with patch("coworker.connectors.github.requests.request", side_effect=fake), patch("time.sleep"):
        with pytest.raises(ConnectorError) as err:
            github.GitHubClient({"access_token": "t"}).login()
    assert err.value.code == "reauth_required" and len(calls) == 2
    with patch("coworker.connectors.github.requests.request", return_value=_resp(404, {})):
        assert github.GitHubClient({"access_token": "t"}).read_file("a/b", "x.py") is None


def test_github_reads_files_tree_and_pull():
    content = base64.b64encode(b"print('hi')\n").decode()

    def fake(method: str, url: str, **kw: Any) -> MagicMock:
        if "/contents/" in url:
            return _resp(200, {"encoding": "base64", "content": content})
        if url.endswith("/repos/a/b"):
            return _resp(200, {"default_branch": "trunk"})
        if "/git/trees/" in url:
            return _resp(200, {"tree": [{"path": "x.py", "type": "blob"}, {"path": "d", "type": "tree"}]})
        if url.endswith("/pulls/3"):
            return _resp(200, {"title": "T", "base": {"ref": "main"}, "head": {"ref": "f", "sha": "s"},
                               "user": {"login": "u"}, "html_url": "h"})
        raise AssertionError(url)

    client = github.GitHubClient({"access_token": "t"})
    with patch("coworker.connectors.github.requests.request", side_effect=fake):
        assert client.read_file("a/b", "x.py") == "print('hi')\n"
        assert client.tree("a/b") == ["x.py"]
        assert client.pull("a/b", 3)["head_sha"] == "s"


def test_github_open_pr_commits_files_on_a_branch_then_undo():
    calls: list[tuple[str, str, Any]] = []

    def fake(method: str, url: str, **kw: Any) -> MagicMock:
        calls.append((method, url, kw.get("json")))
        if url.endswith("/git/ref/heads/main"):
            return _resp(200, {"object": {"sha": "base"}})
        if url.endswith("/git/commits/base"):
            return _resp(200, {"tree": {"sha": "tree0"}})
        if url.endswith("/git/trees"):
            return _resp(201, {"sha": "tree1"})
        if url.endswith("/git/commits"):
            return _resp(201, {"sha": "c1"})
        if url.endswith("/git/refs"):
            return _resp(201, {})
        if url.endswith("/pulls") and method == "POST":
            return _resp(201, {"number": 12, "html_url": "https://github.com/a/b/pull/12"})
        return _resp(200, {})

    client = github.GitHubClient({"access_token": "t"})
    with patch("coworker.connectors.github.requests.request", side_effect=fake):
        out = client.open_pr("a/b", branch="ourogen/x", title="T", body="B", base="main",
                             files=[{"path": "x.py", "content": "1"}, {"path": "old.py", "delete": True}])
        assert out["url"].endswith("/pull/12") and out["undo"]["op"] == "close_pr"
        tree = next(j for m, u, j in calls if u.endswith("/git/trees"))
        assert tree["base_tree"] == "tree0" and tree["tree"][1]["sha"] is None
        assert client.undo(out["undo"])
        assert client.undo({"op": "delete_comment", "repo": "a/b", "id": 1})
        assert client.undo({"op": "close_issue", "repo": "a/b", "number": 2})
        assert not client.undo({"op": "nope"})
        assert client.comment("a/b", 1, "hi")["undo"]["op"] == "delete_comment"
        assert client.create_issue("a/b", "t", "b")["undo"]["op"] == "close_issue"
        client.review("a/b", 1, "body", [{"path": "x.py", "line": 3, "body": "c"}, {"path": "", "line": 0, "body": "skip"}])
    review_call = next(j for m, u, j in calls if u.endswith("/reviews"))
    assert len(review_call["comments"]) == 1 and review_call["event"] == "COMMENT"


def test_github_oauth_exchange_and_revoke(monkeypatch):
    monkeypatch.setenv("GITHUB_CLIENT_ID", "cid")
    monkeypatch.setenv("GITHUB_CLIENT_SECRET", "sec")
    with patch("coworker.connectors.github.requests.post", return_value=_resp(200, {"access_token": "gho_x", "scope": "repo"})), \
         patch("coworker.connectors.github.requests.request", return_value=_resp(200, {"login": "natan"})):
        token = github.exchange_code("code")
    assert token["login"] == "natan" and token["kind"] == "oauth"
    with patch("coworker.connectors.github.requests.post", return_value=_resp(400, {"error_description": "bad code"})):
        with pytest.raises(ConnectorError):
            github.exchange_code("code")
    with patch("coworker.connectors.github.requests.delete") as delete:
        github.revoke(token)
        github.revoke({"kind": "pat"})
    assert delete.call_count == 1


# -- Jira and Notion -----------------------------------------------------------------

def test_jira_verify_sync_and_writes(s):
    def fake(method: str, url: str, **kw: Any) -> MagicMock:
        if url.endswith("/myself"):
            return _resp(200, {"accountId": "me", "displayName": "Natan"})
        if url.endswith("/search/jql"):
            return _resp(200, {"issues": [{"key": "ACME-1", "fields": {
                "summary": "Annual billing", "description": {"type": "doc", "content": [
                    {"type": "paragraph", "content": [{"type": "text", "text": "Two months free"}]}]},
                "status": {"name": "To Do"}, "issuetype": {"name": "Story"}, "assignee": {"accountId": "me"},
                "reporter": {"displayName": "Priya"}, "comment": {"comments": [
                    {"author": {"accountId": "me"}, "body": {"type": "doc", "content": [{"type": "paragraph",
                                                                                          "content": [{"type": "text", "text": "On it"}]}]}}]}}}]})
        if url.endswith("/issue/ACME-1"):
            return _resp(200, {"fields": {"summary": "Annual billing", "description": None, "status": {"name": "To Do"}}})
        if url.endswith("/rest/api/3/issue") and method == "POST":
            return _resp(201, {"key": "ACME-2"})
        if url.endswith("/comment") and method == "POST":
            return _resp(201, {"id": "77"})
        return _resp(204)

    with pytest.raises(ConnectorError):
        jira.verify("http://evil.example.com", "a@b.co", "t" * 20)
    with patch("coworker.connectors.jira.requests.request", side_effect=fake):
        token = jira.verify("acme.atlassian.net/", "n@acme.com", "t" * 20)
        assert token["site"] == "https://acme.atlassian.net" and token["account_id"] == "me"
        client = jira.JiraClient(token)
        assert client.sync(s, 1) == 1
        assert client.issue("ACME-1")["url"].endswith("/browse/ACME-1")
        created = client.create_issue("ACME", "S", "line one\n\nline two")
        assert created["external_id"] == "ACME-2" and client.undo(created["undo"])
        comment = client.comment("ACME-1", "done")
        assert client.undo(comment["undo"]) and not client.undo({"op": "x"})
    item = s.items(1, provider="jira")[0]
    assert item["body"].strip() == "Two months free" and item["meta"]["my_comments"] == ["On it\n"]
    assert jira.text_to_adf("a\nb")["content"][1]["content"][0]["text"] == "b"
    with patch("coworker.connectors.jira.requests.request", return_value=_resp(401, {"errorMessages": ["nope"]})):
        with pytest.raises(ConnectorError) as err:
            jira.JiraClient(token).issue("ACME-1")
    assert err.value.code == "reauth_required"


def test_notion_sync_pages_and_create(s, monkeypatch):
    def fake(method: str, url: str, **kw: Any) -> MagicMock:
        if url.endswith("/users/me"):
            return _resp(200, {"bot": {"workspace_name": "Acme"}})
        if url.endswith("/search"):
            return _resp(200, {"results": [{"id": "p1", "last_edited_time": "2026-01-01T00:00:00Z", "url": "https://n/p1",
                                            "properties": {"Name": {"type": "title", "title": [{"plain_text": "Conventions"}]}}}]})
        if url.endswith("/blocks/p1/children"):
            return _resp(200, {"results": [
                {"type": "heading_1", "heading_1": {"rich_text": [{"plain_text": "Rules"}]}},
                {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"plain_text": "Money is Decimal"}]}},
                {"type": "divider", "divider": {}}]})
        if url.endswith("/pages/p1"):
            return _resp(200, {"properties": {}, "url": "https://n/p1"})
        if url.endswith("/pages") and method == "POST":
            return _resp(200, {"id": "p2", "url": "https://n/p2"})
        return _resp(200, {})

    assert notion.looks_like_token("ntn_" + "x" * 30) and not notion.looks_like_token("ghp_x")
    with patch("coworker.connectors.notion.requests.request", side_effect=fake):
        token = notion.verify_token("ntn_" + "x" * 30)
        assert token["workspace"] == "Acme"
        client = notion.NotionClient(token)
        assert client.sync(s, 1) == 1
        assert client.page("p1")["title"] == "Untitled"
        out = client.create_page("parent", "Spec", "# Title\n- one\n- [ ] todo\ntext")
        assert client.undo(out["undo"]) and not client.undo({"op": "x"})
    assert s.items(1, provider="notion")[0]["body"] == "# Rules\n- Money is Decimal"
    blocks = notion.markdown_to_blocks("## H\n* b\n- [ ] t\np")
    assert [b["type"] for b in blocks] == ["heading_2", "bulleted_list_item", "to_do", "paragraph"]
    monkeypatch.setenv("NOTION_CLIENT_ID", "c")
    monkeypatch.setenv("NOTION_CLIENT_SECRET", "s")
    assert notion.is_configured() and "owner=user" in notion.auth_url("st")
    with patch("coworker.connectors.notion.requests.post", return_value=_resp(200, {"access_token": "a", "workspace_name": "W"})):
        assert notion.exchange_code("c")["workspace"] == "W"
    with patch("coworker.connectors.notion.requests.post", return_value=_resp(400, {"error": "invalid_grant"})):
        with pytest.raises(ConnectorError):
            notion.exchange_code("c")


# -- MCP -----------------------------------------------------------------------------

def _public(*args: Any, **kwargs: Any) -> list:
    return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443))]


def test_mcp_url_checks(monkeypatch):
    monkeypatch.delenv("COWORKER_MCP_ALLOW_PRIVATE", raising=False)
    with pytest.raises(ConnectorError):
        mcp.check_url("http://mcp.example.com")
    with patch("socket.getaddrinfo", return_value=[(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", 443))]):
        with pytest.raises(ConnectorError):
            mcp.check_url("https://localhost/mcp")
    with patch("socket.getaddrinfo", side_effect=socket.gaierror):
        with pytest.raises(ConnectorError):
            mcp.check_url("https://nope.invalid/mcp")
    with patch("socket.getaddrinfo", side_effect=_public):
        assert mcp.check_url("https://mcp.example.com/mcp") == "https://mcp.example.com/mcp"
    monkeypatch.setenv("COWORKER_MCP_ALLOW_PRIVATE", "1")
    assert mcp.check_url("http://localhost:8000/mcp")
    with pytest.raises(ConnectorError):
        mcp.slug("!!!")
    assert mcp.provider_for("Linear Server") == "mcp_linear-server" and mcp.is_mcp("mcp_x")


def _mcp_server(method_calls: list[str]) -> Any:
    def fake(url: str, json: dict, headers: dict, timeout: int) -> MagicMock:
        method_calls.append(json["method"])
        if json["method"] == "initialize":
            return _resp(200, {"jsonrpc": "2.0", "id": json["id"], "result": {"serverInfo": {"name": "Linear"}}},
                         {"Mcp-Session-Id": "sess", "Content-Type": "application/json"})
        if json["method"] == "notifications/initialized":
            return _resp(202)
        if json["method"] == "tools/list":
            assert headers["Mcp-Session-Id"] == "sess" and headers["Authorization"] == "Bearer key"
            return _resp(200, None, {"Content-Type": "text/event-stream"},
                         text='event: message\ndata: {"jsonrpc":"2.0","id":3,"result":{"tools":[{"name":"create_issue",'
                              '"description":"Create","inputSchema":{"type":"object"}}]}}\n\n')
        if json["method"] == "tools/call":
            if json["params"]["name"] == "explode":
                return _resp(200, {"jsonrpc": "2.0", "id": json["id"], "error": {"message": "boom"}})
            return _resp(200, {"jsonrpc": "2.0", "id": json["id"], "result": {
                "content": [{"type": "text", "text": "Created LIN-1"}], "isError": False}}, {"Content-Type": "application/json"})
        raise AssertionError(json["method"])
    return fake


def test_mcp_connect_list_and_call(monkeypatch):
    monkeypatch.setenv("COWORKER_MCP_ALLOW_PRIVATE", "1")
    calls: list[str] = []
    with patch("coworker.connectors.mcp.requests.post", side_effect=_mcp_server(calls)):
        token = mcp.connect("Linear", "http://localhost:9/mcp", "key")
        assert token["server"] == "Linear" and token["tools"][0]["name"] == "create_issue"
        client = mcp.MCPClient(token)
        assert client.call_tool("create_issue", {"title": "x"}) == {"text": "Created LIN-1", "isError": False}
        with pytest.raises(ConnectorError):
            client.call_tool("explode", {})
    assert "notifications/initialized" in calls
    with patch("coworker.connectors.mcp.requests.post", return_value=_resp(401)):
        with pytest.raises(ConnectorError) as err:
            mcp.MCPClient(token).initialize()
    assert err.value.code == "reauth_required"
    with patch("coworker.connectors.mcp.requests.post", return_value=_resp(500)):
        with pytest.raises(ConnectorError):
            mcp.MCPClient(token).initialize()
    import requests as _requests
    with patch("coworker.connectors.mcp.requests.post", side_effect=_requests.ConnectionError("down")):
        with pytest.raises(ConnectorError):
            mcp.MCPClient(token).initialize()


# -- routing, actions, undo ------------------------------------------------------------

def test_demo_client_reads_and_records_writes(s):
    client = devtools.client_for(s, 1, "github")
    assert isinstance(client, devtools.DemoDevClient) and client.login() == "natan-demo"
    assert "app/pricing.py" in client.tree(devtools.REPO) and client.tree("other/repo") == []
    assert client.read_file(devtools.REPO, "app/pricing.py") and client.default_branch("x") == "main"
    assert client.pull(devtools.REPO, 37)["number"] == 37 and client.pr_files(devtools.REPO, 37)
    assert devtools.client_for(s, 1, "jira").issue("ACME-142")["summary"].startswith("Annual billing")
    with pytest.raises(ConnectorError):
        devtools.client_for(s, 1, "jira").issue("NOPE-1")
    assert devtools.client_for(s, 1, "notion").page("eng-conventions")["title"] == "Engineering conventions"
    with pytest.raises(ConnectorError):
        devtools.client_for(s, 1, "notion").page("missing")
    assert devtools.ensure_demo(s, 1) == 0  # already seeded once
    s.update_coworker(1, mode="live")
    assert devtools.client_for(s, 1, "github") is None
    with pytest.raises(ConnectorError) as err:
        devtools.require(s, 1, "github")
    assert err.value.code == "not_connected"


def test_dev_actions_run_through_approvals_and_undo(s):
    s.update_coworker(1, autonomy={"github.comment": "notify"})
    action = executor.propose(s, 1, "github.comment", {"repo": devtools.REPO, "number": 37, "body": "Looks good"},
                              title="Comment")
    assert action["status"] == "executed" and action["result"]["demo"]
    undone = executor.undo(s, 1, action["id"])
    assert undone["status"] == "undone"
    for kind, payload in [("github.issue", {"repo": devtools.REPO, "title": "t", "body": "b"}),
                          ("github.review", {"repo": devtools.REPO, "number": 37, "body": "b", "comments": []}),
                          ("jira.issue", {"project": "ACME", "summary": "s", "description": "d"}),
                          ("jira.comment", {"key": "ACME-142", "body": "b"}),
                          ("notion.page", {"parent_page_id": "p", "title": "t", "markdown": "m"})]:
        proposed = executor.propose(s, 1, kind, payload, title=kind)
        assert proposed["status"] == "proposed"
        assert executor.approve(s, 1, proposed["id"])["status"] == "executed"


def test_live_dev_action_and_undo_use_the_connected_client(s):
    _connect(s, "github", {"access_token": "t", "login": "natan"})
    s.update_coworker(1, mode="live")
    from coworker import governance

    governance.authorize(s, 1, governance.BASES[0])
    with patch("coworker.connectors.github.GitHubClient.comment",
               return_value={"external_id": "9", "url": "u", "undo": {"provider": "github", "op": "delete_comment",
                                                                       "repo": "a/b", "id": 9}}), \
         patch("coworker.connectors.github.GitHubClient.undo", return_value=True) as undo:
        action = executor.propose(s, 1, "github.comment", {"repo": "a/b", "number": 1, "body": "x"}, title="c")
        executor.approve(s, 1, action["id"])
        executor.undo(s, 1, action["id"])
    assert undo.called
    assert devtools.undo(s, 1, {"provider": "jira", "op": "x"}) is False
    assert devtools.connected(s, 1) == ["github"]


def test_mcp_call_action(s, monkeypatch):
    monkeypatch.setenv("COWORKER_MCP_ALLOW_PRIVATE", "1")
    _connect(s, "mcp_linear", {"kind": "mcp", "name": "linear", "url": "http://localhost:9/mcp", "auth": "key",
                               "tools": [{"name": "create_issue"}]})
    calls: list[str] = []
    with patch("coworker.connectors.mcp.requests.post", side_effect=_mcp_server(calls)):
        action = executor.propose(s, 1, "mcp.call", {"server": "linear", "tool": "create_issue", "arguments": {}},
                                  title="Run it")
        done = executor.approve(s, 1, action["id"])
    assert done["status"] == "executed" and done["result"]["output"] == "Created LIN-1"
    with pytest.raises(ConnectorError):
        devtools.execute(s, 1, "mcp.call", {"server": "missing", "tool": "x"})
    with patch("coworker.connectors.mcp.requests.post", side_effect=_mcp_server([])):
        with pytest.raises(ConnectorError):
            devtools.execute(s, 1, "mcp.call", {"server": "linear", "tool": "explode"})


def test_devtools_sync_marks_errors_per_connection(s):
    _connect(s, "github", {"access_token": "t"})
    _connect(s, "jira", {"site": "https://a.atlassian.net"})
    with patch("coworker.connectors.github.GitHubClient.sync", return_value=4), \
         patch("coworker.connectors.jira.JiraClient.sync", side_effect=ConnectorError("expired", "reauth_required")):
        assert devtools.sync(s, 1) == {"github": 4}
    assert s.get_connection_row(1, "jira")["status"] == "reauth_required"
    assert s.get_connection_row(1, "github")["status"] == "connected"


# -- routes ------------------------------------------------------------------------------

def test_connect_routes(client, auth_headers, monkeypatch):
    h = auth_headers
    assert client.post("/api/coworker/connections/github/token", json={"token": "ghp_" + "a" * 36}, headers=h).status_code == 404
    client.post("/api/coworker", json={"mode": "demo"}, headers=h)
    assert client.post("/api/coworker/connections/github/token", json={"token": "nope"}, headers=h).status_code == 400
    with patch("coworker.connectors.github.verify_token", return_value={"access_token": "ghp_x", "login": "natan"}), \
         patch("coworker.connectors.devtools.sync", return_value={}):
        resp = client.post("/api/coworker/connections/github/token", json={"token": "ghp_" + "a" * 36}, headers=h)
    assert resp.status_code == 200 and resp.get_json()["account"] == "natan"
    with patch("coworker.connectors.github.verify_token", side_effect=ConnectorError("bad", "invalid")):
        assert client.post("/api/coworker/connections/github/token", json={"token": "ghp_" + "a" * 36},
                           headers=h).status_code == 400
    with patch("coworker.connectors.notion.verify_token", return_value={"access_token": "n", "workspace": "Acme"}), \
         patch("coworker.connectors.devtools.sync", side_effect=RuntimeError("first sync failed")):
        assert client.post("/api/coworker/connections/notion/token", json={"token": "ntn_" + "x" * 30},
                           headers=h).status_code == 200
    assert client.post("/api/coworker/connections/notion/token", json={"token": "x"}, headers=h).status_code == 400
    assert client.post("/api/coworker/connections/jira/token", json={"site": "a"}, headers=h).status_code == 400
    with patch("coworker.connectors.jira.verify", return_value={"site": "https://a.atlassian.net", "name": "N"}), \
         patch("coworker.connectors.devtools.sync", return_value={}):
        assert client.post("/api/coworker/connections/jira/token",
                           json={"site": "a.atlassian.net", "email": "n@a.co", "token": "t" * 20}, headers=h).status_code == 200
    with patch("coworker.connectors.jira.verify", side_effect=ConnectorError("bad")):
        assert client.post("/api/coworker/connections/jira/token",
                           json={"site": "a.atlassian.net", "email": "n@a.co", "token": "t" * 20}, headers=h).status_code == 400
    with patch("coworker.connectors.notion.verify_token", side_effect=ConnectorError("bad")):
        assert client.post("/api/coworker/connections/notion/token", json={"token": "ntn_" + "x" * 30},
                           headers=h).status_code == 400
    conns = {c["provider"]: c for c in client.get("/api/coworker/connections", headers=h).get_json()["connections"]}
    assert {"github", "notion", "jira"} <= set(conns)
    caps = client.get("/api/coworker", headers=h).get_json()["capabilities"]
    assert caps["github_oauth"] is False and caps["notion_oauth"] is False
    for provider in ("github", "notion"):
        monkeypatch.delenv(f"{provider.upper()}_CLIENT_ID", raising=False)
        assert client.post(f"/api/coworker/connections/{provider}/start", headers=h).status_code == 501
    resp = client.delete("/api/coworker/connections/github", headers=h)
    assert resp.status_code == 200


def test_oauth_callbacks(client, auth_headers, monkeypatch):
    h = auth_headers
    client.post("/api/coworker", json={"mode": "demo"}, headers=h)
    for provider in ("github", "notion"):
        monkeypatch.setenv(f"{provider.upper()}_CLIENT_ID", "cid")
        monkeypatch.setenv(f"{provider.upper()}_CLIENT_SECRET", "sec")
        url = client.post(f"/api/coworker/connections/{provider}/start", headers=h).get_json()["url"]
        state = url.split("state=")[1].split("&")[0]
        from urllib.parse import unquote
        state = unquote(state)
        token = {"access_token": "x", "login": "natan", "workspace": "Acme"}
        with patch(f"coworker.connectors.{provider}.exchange_code", return_value=token), \
             patch("coworker.connectors.devtools.sync", return_value={}):
            landed = oauth_return(client, f"/api/coworker/connections/{provider}/callback?code=c&state={state}")
        assert f"connected={provider}" in landed.location
        with patch(f"coworker.connectors.{provider}.exchange_code", side_effect=ConnectorError("denied")):
            landed = oauth_return(client, f"/api/coworker/connections/{provider}/callback?code=c&state={state}")
        assert "connect_error" in landed.location
        landed = oauth_return(client, f"/api/coworker/connections/{provider}/callback?code=c&state=bad")
        assert "connect_error" in landed.location


def test_mcp_routes(client, auth_headers, monkeypatch):
    h = auth_headers
    monkeypatch.setenv("COWORKER_MCP_ALLOW_PRIVATE", "1")
    assert client.post("/api/coworker/connections/mcp", json={"name": "Linear", "url": "http://localhost:9/mcp"},
                       headers=h).status_code == 404
    client.post("/api/coworker", json={"mode": "demo"}, headers=h)
    assert client.post("/api/coworker/connections/mcp", json={"name": ""}, headers=h).status_code == 400
    with patch("coworker.connectors.mcp.requests.post", side_effect=_mcp_server([])):
        resp = client.post("/api/coworker/connections/mcp", json={"name": "Linear", "url": "http://localhost:9/mcp",
                                                                  "auth": "key"}, headers=h)
    assert resp.status_code == 200 and resp.get_json()["provider"] == "mcp_linear"
    conns = {c["provider"]: c for c in client.get("/api/coworker/connections", headers=h).get_json()["connections"]}
    assert conns["mcp_linear"]["tools"] == ["create_issue"] and conns["mcp_linear"]["name"] == "Linear"
    assert client.get("/api/coworker/mcp/linear/tools", headers=h).get_json()["tools"][0]["name"] == "create_issue"
    assert client.get("/api/coworker/mcp/nope/tools", headers=h).status_code == 404
    assert client.post("/api/coworker/mcp/nope/call", json={"tool": "x"}, headers=h).status_code == 404
    assert client.post("/api/coworker/mcp/linear/call", json={"tool": "missing"}, headers=h).status_code == 404
    resp = client.post("/api/coworker/mcp/linear/call", json={"tool": "create_issue", "arguments": {"title": "t"}}, headers=h)
    assert resp.status_code == 201 and resp.get_json()["action"]["type"] == "mcp.call"
    assert resp.get_json()["action"]["status"] == "proposed"
    with patch("coworker.connectors.mcp.requests.post", return_value=_resp(500)):
        assert client.post("/api/coworker/connections/mcp", json={"name": "Bad", "url": "http://localhost:9/mcp"},
                           headers=h).status_code == 400
    assert client.delete("/api/coworker/connections/mcp_linear", headers=h).status_code == 200


def test_sync_route_runs_dev_tools_in_demo_mode(client, auth_headers):
    h = auth_headers
    client.post("/api/coworker", json={"mode": "demo"}, headers=h)
    with patch("coworker.connectors.github.verify_token", return_value={"access_token": "ghp_x", "login": "natan"}), \
         patch("coworker.connectors.devtools.sync", return_value={}):
        client.post("/api/coworker/connections/github/token", json={"token": "ghp_" + "a" * 36}, headers=h)
    with patch("coworker.connectors.devtools.sync", return_value={"github": 2}) as sync:
        assert client.post("/api/coworker/sync", headers=h).status_code == 200
    assert sync.called


def test_token_round_trip():
    assert decrypt_token(encrypt_token({"a": 1})) == {"a": 1}
