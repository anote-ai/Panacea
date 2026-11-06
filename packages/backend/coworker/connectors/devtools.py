"""Developer tools: GitHub, Jira, Notion, and any MCP server.

``client_for(store, user_id, provider)`` returns the live client when the user
connected that tool, the demo client when the coworker is in demo mode, and
otherwise ``None``. Every write goes through an approved action
(``github.*``, ``jira.*``, ``notion.page``, ``mcp.call``); ``execute`` runs one
and ``undo`` reverses it where the tool allows.
"""
from __future__ import annotations

import itertools
from typing import Any

from coworker.connectors.base import ConnectorError, decrypt_token, encrypt_token
from coworker.connectors.devtools_demo import FILES, LOGIN, PAGES, REPO, TICKET, seed_items
from coworker.store import Store, iso, utcnow

PROVIDERS = ("github", "jira", "notion")
LABELS = {"github": "GitHub", "jira": "Jira", "notion": "Notion"}
SYNCED = {"github": ("github",), "jira": ("jira",), "notion": ("notion",)}

ACTIONS: dict[str, dict[str, Any]] = {
    "github.comment": {"label": "Comment on GitHub", "external": False, "provider": "github"},
    "github.issue": {"label": "Open a GitHub issue", "external": False, "provider": "github"},
    "github.review": {"label": "Post a code review", "external": False, "provider": "github"},
    "github.pr": {"label": "Open a pull request", "external": False, "provider": "github"},
    "jira.issue": {"label": "Create a Jira issue", "external": False, "provider": "jira"},
    "jira.comment": {"label": "Comment on Jira", "external": False, "provider": "jira"},
    "notion.page": {"label": "Write a Notion page", "external": False, "provider": "notion"},
    "mcp.call": {"label": "Use an MCP tool", "external": False, "provider": "mcp"},
}


def _client_class(provider: str) -> Any:
    from coworker.connectors.github import GitHubClient
    from coworker.connectors.jira import JiraClient
    from coworker.connectors.mcp import MCPClient, is_mcp
    from coworker.connectors.notion import NotionClient

    if is_mcp(provider):
        return MCPClient
    return {"github": GitHubClient, "jira": JiraClient, "notion": NotionClient}[provider]


def live_client(store: Store, user_id: int, provider: str) -> Any | None:
    row = store.get_connection_row(user_id, provider)
    if not row or row.get("status") not in ("connected", "syncing"):
        return None

    def save(token: dict[str, Any]) -> None:
        store.upsert_connection(user_id, provider, token_enc=encrypt_token(token))

    return _client_class(provider)(decrypt_token(row.get("token_enc")), on_refresh=save)


def client_for(store: Store, user_id: int, provider: str) -> Any | None:
    client = live_client(store, user_id, provider)
    if client:
        return client
    if (store.get_coworker(user_id) or {}).get("mode", "demo") == "demo" and provider in PROVIDERS:
        ensure_demo(store, user_id)
        return DemoDevClient(provider)
    return None


def require(store: Store, user_id: int, provider: str) -> Any:
    client = client_for(store, user_id, provider)
    if client is None:
        raise ConnectorError(f"Connect {LABELS.get(provider, provider)} in Settings first.", "not_connected")
    return client


def connected(store: Store, user_id: int) -> list[str]:
    return [r["provider"] for r in store.list_connections(user_id)
            if (r["provider"] in PROVIDERS or r["provider"].startswith("mcp_")) and r.get("status") in ("connected", "syncing")]


def ensure_demo(store: Store, user_id: int) -> int:
    """Seed the fictional repo, tickets and docs once per demo workspace."""
    if store.one("SELECT id FROM cw_items WHERE user_id = %s AND provider = 'github' AND external_id = %s",
                 (user_id, f"pr:{REPO}#{28}")):
        return 0
    return sum(1 for item in seed_items(utcnow()) if store.add_item(user_id, item))


def sync(store: Store, user_id: int) -> dict[str, int]:
    """Sync every connected dev tool. Errors mark that connection, never the others."""
    counts: dict[str, int] = {}
    for provider in PROVIDERS:
        client = live_client(store, user_id, provider)
        if not client:
            continue
        try:
            counts[provider] = client.sync(store, user_id)
            store.upsert_connection(user_id, provider, status="connected", error="", last_synced_at=iso())
        except ConnectorError as exc:
            status = "reauth_required" if exc.code == "reauth_required" else "error"
            store.upsert_connection(user_id, provider, status=status, error=str(exc)[:500])
    return counts


def purge(store: Store, user_id: int, provider: str) -> int:
    return sum(store.delete_items(user_id, p) for p in SYNCED.get(provider, ()))


def _mcp_client(store: Store, user_id: int, server: str) -> Any:
    from coworker.connectors.mcp import provider_for

    client = live_client(store, user_id, provider_for(server))
    if not client:
        raise ConnectorError(f"The MCP server '{server}' isn't connected.", "not_connected")
    return client


def execute(store: Store, user_id: int, kind: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Run an approved dev-tool action and return its result (with ``undo`` info where possible)."""
    if kind == "mcp.call":
        out = _mcp_client(store, user_id, payload.get("server", "")).call_tool(payload.get("tool", ""),
                                                                                payload.get("arguments") or {})
        if out.get("isError"):
            raise ConnectorError(f"The MCP tool failed: {out.get('text', '')[:300]}", "provider_error")
        return {"output": out.get("text", ""), "undo": {}}
    client = require(store, user_id, ACTIONS[kind]["provider"])
    if kind == "github.comment":
        return dict(client.comment(payload["repo"], int(payload["number"]), payload.get("body", "")))
    if kind == "github.issue":
        return dict(client.create_issue(payload["repo"], payload.get("title", ""), payload.get("body", ""),
                                        payload.get("labels") or []))
    if kind == "github.review":
        return dict(client.review(payload["repo"], int(payload["number"]), payload.get("body", ""),
                                  payload.get("comments") or [], payload.get("event", "COMMENT")))
    if kind == "github.pr":
        return dict(client.open_pr(payload["repo"], branch=payload["branch"], title=payload.get("title", ""),
                                   body=payload.get("body", ""), files=payload.get("files") or [],
                                   base=payload.get("base", "")))
    if kind == "jira.issue":
        return dict(client.create_issue(payload["project"], payload.get("summary", ""), payload.get("description", ""),
                                        payload.get("issuetype", "Task")))
    if kind == "jira.comment":
        return dict(client.comment(payload["key"], payload.get("body", "")))
    if kind == "notion.page":
        return dict(client.create_page(payload["parent_page_id"], payload.get("title", ""), payload.get("markdown", "")))
    raise ConnectorError(f"Don't know how to run {kind}", "bad_request")  # pragma: no cover


def undo(store: Store, user_id: int, info: dict[str, Any]) -> bool:
    provider = info.get("provider", "")
    if provider == "demo":
        return True
    client = live_client(store, user_id, provider) if provider in PROVIDERS else None
    return bool(client and client.undo(info))


_demo_ids = itertools.count(500)


class DemoDevClient:
    """Reads come from the fictional repo; writes are recorded in the workspace, never sent."""

    def __init__(self, provider: str) -> None:
        self.provider = provider
        self.label = f"{LABELS[provider]} (demo)"

    def login(self) -> str:
        return LOGIN

    def default_branch(self, repo: str) -> str:
        return "main"

    def tree(self, repo: str, ref: str = "") -> list[str]:
        return sorted(FILES) if repo == REPO else []

    def read_file(self, repo: str, path: str, ref: str = "") -> str | None:
        return FILES.get(path) if repo == REPO else None

    def pull(self, repo: str, number: int) -> dict[str, Any]:
        return {"number": number, "title": f"Demo PR #{number}", "body": "", "base": "main", "head": f"demo-{number}",
                "head_sha": "", "author": "teammate", "url": f"https://github.com/{repo}/pull/{number}"}

    def pr_files(self, repo: str, number: int) -> list[dict[str, Any]]:
        from coworker.engineering.demo import DEMO_REVIEW_PATCH

        return [dict(f) for f in DEMO_REVIEW_PATCH]

    def issue(self, key: str) -> dict[str, Any]:
        if key == TICKET["key"]:
            return dict(TICKET)
        raise ConnectorError(f"No demo ticket {key}", "not_found")

    def page(self, page_id: str) -> dict[str, Any]:
        for title, pid, text in PAGES:
            if pid == page_id:
                return {"id": pid, "title": title, "text": text, "url": f"https://www.notion.so/demo/{pid}"}
        raise ConnectorError(f"No demo page {page_id}", "not_found")

    def _record(self, what: str, url: str) -> dict[str, Any]:
        n = next(_demo_ids)
        return {"external_id": str(n), "url": url.format(n=n), "demo": True, "summary": what,
                "undo": {"provider": "demo"}}

    def comment(self, target: str, *args: Any) -> dict[str, Any]:
        if self.provider == "jira":  # comment(key, body)
            return self._record("comment", f"https://acme-demo.atlassian.net/browse/{target}?focusedCommentId={{n}}")
        return self._record("comment", f"https://github.com/{target}/pull/{args[0]}#issuecomment-{{n}}")

    def create_issue(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        if self.provider == "jira":
            return self._record("issue", "https://acme-demo.atlassian.net/browse/ACME-{n}")
        return self._record("issue", f"https://github.com/{args[0]}/issues/{{n}}")

    def review(self, repo: str, number: int, body: str, comments: list[dict[str, Any]],
               event: str = "COMMENT") -> dict[str, Any]:
        return self._record("review", f"https://github.com/{repo}/pull/{number}#pullrequestreview-{{n}}")

    def open_pr(self, repo: str, *, branch: str, title: str, body: str, files: list[dict[str, Any]],
                base: str = "") -> dict[str, Any]:
        out = self._record("pull request", f"https://github.com/{repo}/pull/{{n}}")
        return {**out, "branch": branch, "base": base or "main"}

    def create_page(self, parent_page_id: str, title: str, markdown: str) -> dict[str, Any]:
        return self._record("page", "https://www.notion.so/demo/page-{n}")

    def undo(self, info: dict[str, Any]) -> bool:
        return True
