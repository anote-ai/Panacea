"""Connect GitHub, Jira, Notion and MCP servers; call MCP tools through approvals."""
from __future__ import annotations

from typing import Any

from flask import jsonify, request

from api_endpoints.coworker import connections
from api_endpoints.coworker.common import coworker_bp, error, store, uid
from coworker import executor
from coworker.connectors import devtools, github, jira, mcp, notion
from coworker.connectors.base import ConnectorError, decrypt_token, encrypt_token
from middleware.auth import require_auth


def _save(user_id: int, provider: str, token: dict[str, Any], account: str) -> None:
    s = store()
    s.upsert_connection(user_id, provider, account_label=account[:255], token_enc=encrypt_token(token),
                        scopes=str(token.get("scope", "")), status="connected", error="")
    s.log(user_id, "connection", f"Connected {devtools.LABELS.get(provider, provider)} ({account})")
    try:  # first sync right away, so the knowledge pack has something to learn from
        devtools.sync(s, user_id)
    except Exception:  # a failed first sync shows on the connection; never fail the connect
        pass


def _body() -> dict[str, Any]:
    return request.get_json(silent=True) or {}


def _need_coworker() -> tuple | None:
    if not store().get_coworker(uid()):
        return error("Set up your coworker first", 404, "not_found")
    return None


# -- GitHub -------------------------------------------------------------------

@coworker_bp.post("/connections/github/start")
@require_auth
def github_start() -> tuple:
    if not github.is_configured():
        return error("GitHub OAuth isn't configured. Paste a personal access token instead, or set GITHUB_CLIENT_ID "
                     "and GITHUB_CLIENT_SECRET.", 501, "not_configured")
    return jsonify({"url": github.auth_url(connections._state(uid(), "github"))}), 200


def github_callback() -> Any:
    state = connections._read_state(connections._args().get("state", ""), "github")
    if not state:
        return connections._back("github", False, "invalid or expired state")
    try:
        token = github.exchange_code(connections._args().get("code", ""))
    except ConnectorError as exc:
        return connections._back("github", False, str(exc))
    _save(int(state["uid"]), "github", token, token.get("login", "GitHub"))
    return connections._back("github", True)


@coworker_bp.post("/connections/github/token")
@require_auth
def github_token() -> tuple:
    value = str(_body().get("token", "")).strip()
    if not github.looks_like_token(value):
        return error("Paste a GitHub personal access token (it starts with ghp_ or github_pat_)")
    if (missing := _need_coworker()) is not None:
        return missing
    try:
        token = github.verify_token(value)
    except ConnectorError as exc:
        return error(str(exc), 400, "invalid_token")
    _save(uid(), "github", token, token["login"])
    return jsonify({"connected": True, "account": token["login"]}), 200


# -- Notion -------------------------------------------------------------------

@coworker_bp.post("/connections/notion/start")
@require_auth
def notion_start() -> tuple:
    if not notion.is_configured():
        return error("Notion OAuth isn't configured. Paste an integration secret instead, or set NOTION_CLIENT_ID "
                     "and NOTION_CLIENT_SECRET.", 501, "not_configured")
    return jsonify({"url": notion.auth_url(connections._state(uid(), "notion"))}), 200


def notion_callback() -> Any:
    state = connections._read_state(connections._args().get("state", ""), "notion")
    if not state:
        return connections._back("notion", False, "invalid or expired state")
    try:
        token = notion.exchange_code(connections._args().get("code", ""))
    except ConnectorError as exc:
        return connections._back("notion", False, str(exc))
    _save(int(state["uid"]), "notion", token, token.get("workspace", "Notion"))
    return connections._back("notion", True)


@coworker_bp.post("/connections/notion/token")
@require_auth
def notion_token() -> tuple:
    value = str(_body().get("token", "")).strip()
    if not notion.looks_like_token(value):
        return error("Paste a Notion integration secret (it starts with ntn_ or secret_)")
    if (missing := _need_coworker()) is not None:
        return missing
    try:
        token = notion.verify_token(value)
    except ConnectorError as exc:
        return error(str(exc), 400, "invalid_token")
    _save(uid(), "notion", token, token["workspace"])
    return jsonify({"connected": True, "account": token["workspace"]}), 200


# -- Jira ---------------------------------------------------------------------

@coworker_bp.post("/connections/jira/token")
@require_auth
def jira_token() -> tuple:
    data = _body()
    site, email, value = (str(data.get(k, "")).strip() for k in ("site", "email", "token"))
    if not (site and "@" in email and len(value) >= 16):
        return error("Enter your Jira site, your Atlassian email, and an API token")
    if (missing := _need_coworker()) is not None:
        return missing
    try:
        token = jira.verify(site, email, value)
    except ConnectorError as exc:
        return error(str(exc), 400, "invalid_token")
    _save(uid(), "jira", token, f"{token['site'].removeprefix('https://')} ({token['name']})")
    return jsonify({"connected": True, "account": token["site"]}), 200


# -- MCP servers --------------------------------------------------------------

@coworker_bp.post("/connections/mcp")
@require_auth
def mcp_connect() -> tuple:
    data = _body()
    name, url = str(data.get("name", "")).strip(), str(data.get("url", "")).strip()
    if not name or not url:
        return error("Give the server a name and its URL")
    if (missing := _need_coworker()) is not None:
        return missing
    try:
        provider = mcp.provider_for(name)
        token = mcp.connect(name, url, str(data.get("auth", "")))
    except ConnectorError as exc:
        return error(str(exc), 400, exc.code)
    s = store()
    s.upsert_connection(uid(), provider, account_label=f"{token['server']} ({len(token['tools'])} tools)"[:255],
                        token_enc=encrypt_token(token), scopes=",".join(t["name"] for t in token["tools"])[:5000],
                        status="connected", error="")
    s.log(uid(), "connection", f"Connected MCP server {name} with {len(token['tools'])} tools")
    return jsonify({"connected": True, "provider": provider, "tools": token["tools"]}), 200


@coworker_bp.get("/mcp/<server>/tools")
@require_auth
def mcp_tools(server: str) -> tuple:
    row = store().get_connection_row(uid(), mcp.provider_for(server))
    if not row:
        return error("Not connected", 404, "not_found")
    return jsonify({"tools": decrypt_token(row.get("token_enc")).get("tools") or []}), 200


@coworker_bp.post("/mcp/<server>/call")
@require_auth
def mcp_call(server: str) -> tuple:
    """Propose an MCP tool call. It runs once approved (or right away, if autonomy allows)."""
    data = _body()
    row = store().get_connection_row(uid(), mcp.provider_for(server))
    if not row:
        return error("Not connected", 404, "not_found")
    tool = str(data.get("tool", ""))
    known = {t.get("name") for t in decrypt_token(row.get("token_enc")).get("tools") or []}
    if tool not in known:
        return error(f"The server has no tool named '{tool}'", 404, "not_found")
    action = executor.propose(store(), uid(), "mcp.call",
                              {"server": server, "tool": tool, "arguments": data.get("arguments") or {}},
                              title=f"Run {tool} on {server}", reasoning=str(data.get("reason", ""))[:1000],
                              requested_in_chat=True)
    return jsonify({"action": executor.serialize(action)}), 201


connections.COMPLETE.update({"github": github_callback, "notion": notion_callback})
