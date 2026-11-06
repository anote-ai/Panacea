"""Notion: docs the coworker reads for knowledge and specs, and pages it writes when approved.

Two ways to connect:

* OAuth (``NOTION_CLIENT_ID`` / ``NOTION_CLIENT_SECRET``) from a Notion public integration.
* Paste an internal integration secret (``ntn_…`` or ``secret_…``) and share the
  pages you want it to see with that integration.

Sync reads the pages the integration can see (title and text). Writes (create a
page) only run as approved actions.
"""
from __future__ import annotations

import os
import time
from typing import Any
from urllib.parse import urlencode

import requests

from coworker.connectors.base import ConnectorError
from coworker.store import Store, iso

API = "https://api.notion.com/v1"
VERSION = "2022-06-28"
TIMEOUT = 20
SYNC_PAGES = 50
BLOCKS_PER_PAGE = 100


def is_configured() -> bool:
    return bool(os.environ.get("NOTION_CLIENT_ID") and os.environ.get("NOTION_CLIENT_SECRET"))


def redirect_uri() -> str:
    default = f"{os.environ.get('BACKEND_URL', 'http://localhost:5000').rstrip('/')}/api/coworker/connections/notion/callback"
    return os.environ.get("NOTION_REDIRECT_URI", default)


def auth_url(state: str) -> str:
    return f"{API}/oauth/authorize?" + urlencode({
        "client_id": os.environ.get("NOTION_CLIENT_ID", ""), "redirect_uri": redirect_uri(), "response_type": "code",
        "owner": "user", "state": state})


def exchange_code(code: str) -> dict[str, Any]:
    resp = requests.post(f"{API}/oauth/token", json={"grant_type": "authorization_code", "code": code,
                                                    "redirect_uri": redirect_uri()},
                         auth=(os.environ.get("NOTION_CLIENT_ID", ""), os.environ.get("NOTION_CLIENT_SECRET", "")),
                         timeout=TIMEOUT)
    body: dict[str, Any] = resp.json() if resp.content else {}
    if resp.status_code >= 400 or not body.get("access_token"):
        raise ConnectorError(f"Notion sign-in failed: {body.get('error') or resp.status_code}", "oauth_failed")
    return {"kind": "oauth", "access_token": body["access_token"], "workspace": body.get("workspace_name") or "Notion"}


def looks_like_token(value: str) -> bool:
    return value.startswith(("ntn_", "secret_")) and len(value) >= 20


def verify_token(value: str) -> dict[str, Any]:
    token: dict[str, Any] = {"kind": "internal", "access_token": value}
    me = NotionClient(token).request("GET", "/users/me")
    token["workspace"] = ((me.get("bot") or {}).get("workspace_name")) or me.get("name") or "Notion"
    return token


def _plain(rich: list[dict[str, Any]] | None) -> str:
    return "".join(r.get("plain_text", "") for r in rich or [])


def page_title(page: dict[str, Any]) -> str:
    for prop in (page.get("properties") or {}).values():
        if prop.get("type") == "title":
            return _plain(prop.get("title"))
    return "Untitled"


def blocks_to_text(blocks: list[dict[str, Any]]) -> str:
    lines = []
    for b in blocks:
        data = b.get(b.get("type", ""), {}) or {}
        text = _plain(data.get("rich_text"))
        if not text:
            continue
        prefix = {"heading_1": "# ", "heading_2": "## ", "heading_3": "### ", "bulleted_list_item": "- ",
                  "numbered_list_item": "1. ", "to_do": "- [ ] "}.get(b.get("type", ""), "")
        lines.append(prefix + text)
    return "\n".join(lines)


def markdown_to_blocks(markdown: str) -> list[dict[str, Any]]:
    blocks = []
    for line in markdown.splitlines():
        if not line.strip():
            continue
        kind, text = "paragraph", line
        for prefix, k in (("### ", "heading_3"), ("## ", "heading_2"), ("# ", "heading_1"), ("- [ ] ", "to_do"),
                          ("- ", "bulleted_list_item"), ("* ", "bulleted_list_item")):
            if line.startswith(prefix):
                kind, text = k, line[len(prefix):]
                break
        body: dict[str, Any] = {"rich_text": [{"type": "text", "text": {"content": text[:2000]}}]}
        if kind == "to_do":
            body["checked"] = False
        blocks.append({"object": "block", "type": kind, kind: body})
    return blocks[:100]


class NotionClient:
    label = "Notion"
    provider = "notion"

    def __init__(self, token: dict[str, Any], on_refresh: Any = None) -> None:
        self.token = token

    def request(self, method: str, path: str, **kwargs: Any) -> Any:
        headers = {"Authorization": f"Bearer {self.token.get('access_token', '')}", "Notion-Version": VERSION}
        for attempt in range(3):
            resp = requests.request(method, f"{API}{path}", headers=headers, timeout=TIMEOUT, **kwargs)
            if resp.status_code == 429 and attempt < 2:
                time.sleep(min(float(resp.headers.get("Retry-After", "1")), 5))
                continue
            body = resp.json() if resp.content else {}
            if resp.status_code >= 400:
                code = "reauth_required" if resp.status_code == 401 else "provider_error"
                raise ConnectorError(f"Notion {method} {path} failed: {body.get('message') or resp.status_code}", code)
            return body
        raise ConnectorError("Notion is rate limiting requests. Try again in a minute.", "rate_limited")  # pragma: no cover

    def page_text(self, page_id: str) -> str:
        body = self.request("GET", f"/blocks/{page_id}/children", params={"page_size": BLOCKS_PER_PAGE})
        return blocks_to_text(body.get("results") or [])

    def page(self, page_id: str) -> dict[str, Any]:
        page = self.request("GET", f"/pages/{page_id}")
        return {"id": page_id, "title": page_title(page), "text": self.page_text(page_id), "url": page.get("url", "")}

    def sync(self, store: Store, user_id: int) -> int:
        body = self.request("POST", "/search", json={"filter": {"property": "object", "value": "page"},
                                                     "sort": {"direction": "descending", "timestamp": "last_edited_time"},
                                                     "page_size": SYNC_PAGES})
        count = 0
        for page in body.get("results") or []:
            try:
                text = self.page_text(page["id"])
            except ConnectorError:
                text = ""
            count += bool(store.add_item(user_id, {
                "provider": "notion", "external_id": f"page:{page['id']}:{page.get('last_edited_time', '')}",
                "kind": "page", "thread_id": f"notion:{page['id']}", "direction": "outbound",
                "subject": page_title(page)[:500], "body": text, "channel": "notion",
                "occurred_at": page.get("last_edited_time") or iso(), "meta": {"url": page.get("url", "")},
            }))
        return count

    def create_page(self, parent_page_id: str, title: str, markdown: str) -> dict[str, Any]:
        out = self.request("POST", "/pages", json={
            "parent": {"page_id": parent_page_id},
            "properties": {"title": {"title": [{"type": "text", "text": {"content": title[:200]}}]}},
            "children": markdown_to_blocks(markdown)})
        return {"external_id": out.get("id", ""), "url": out.get("url", ""),
                "undo": {"provider": "notion", "op": "archive_page", "id": out.get("id")}}

    def undo(self, info: dict[str, Any]) -> bool:
        if info.get("op") == "archive_page":
            self.request("PATCH", f"/pages/{info['id']}", json={"archived": True})
            return True
        return False
