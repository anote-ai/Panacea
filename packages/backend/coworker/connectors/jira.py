"""Jira Cloud: tickets the coworker reads for specs and history, and updates when approved.

Connect with your site (``https://acme.atlassian.net``), your Atlassian email and
an API token (id.atlassian.com → Security → API tokens). Sync reads tickets you
are assigned to or reported, with the comments you wrote. Writes (create an
issue, comment) only run as approved actions.
"""
from __future__ import annotations

import re
import time
from typing import Any

import requests

from coworker.connectors.base import ConnectorError
from coworker.store import Store, iso

TIMEOUT = 20
SYNC_LIMIT = 50
SITE_RE = re.compile(r"^https://[a-z0-9][a-z0-9-]*\.atlassian\.net$")


def normalize_site(value: str) -> str:
    site = value.strip().rstrip("/")
    if not site.startswith("https://"):
        site = f"https://{site.removeprefix('http://')}"
    return site.lower()


def verify(site: str, email: str, api_token: str) -> dict[str, Any]:
    site = normalize_site(site)
    if not SITE_RE.match(site):
        raise ConnectorError("Use your Jira Cloud address, like https://acme.atlassian.net", "bad_request")
    token = {"kind": "api_token", "site": site, "email": email.strip(), "api_token": api_token.strip()}
    me = JiraClient(token).request("GET", "/rest/api/3/myself")
    token["account_id"] = me.get("accountId", "")
    token["name"] = me.get("displayName", email)
    return token


def adf_to_text(node: Any) -> str:
    """Atlassian Document Format → plain text (paragraphs on their own lines)."""
    if node is None:
        return ""
    if isinstance(node, str):
        return node
    if isinstance(node, list):
        return "".join(adf_to_text(n) for n in node)
    if node.get("type") == "text":
        return str(node.get("text", ""))
    inner = adf_to_text(node.get("content") or [])
    return f"{inner}\n" if node.get("type") in ("paragraph", "heading", "listItem", "codeBlock") else inner


def text_to_adf(text: str) -> dict[str, Any]:
    paragraphs = [p for p in text.split("\n") if p.strip()] or [""]
    return {"type": "doc", "version": 1, "content": [
        {"type": "paragraph", "content": [{"type": "text", "text": p}] if p else []} for p in paragraphs]}


class JiraClient:
    label = "Jira"
    provider = "jira"

    def __init__(self, token: dict[str, Any], on_refresh: Any = None) -> None:
        self.token = token

    def request(self, method: str, path: str, **kwargs: Any) -> Any:
        url = f"{self.token.get('site', '')}{path}"
        auth = (self.token.get("email", ""), self.token.get("api_token", ""))
        for attempt in range(3):
            resp = requests.request(method, url, auth=auth, headers={"Accept": "application/json"}, timeout=TIMEOUT,
                                    **kwargs)
            if resp.status_code == 429 and attempt < 2:
                time.sleep(min(float(resp.headers.get("Retry-After", "1")), 5))
                continue
            body = resp.json() if resp.content else {}
            if resp.status_code >= 400:
                code = "reauth_required" if resp.status_code in (401, 403) else "provider_error"
                messages = body.get("errorMessages") if isinstance(body, dict) else None
                raise ConnectorError(f"Jira {method} {path} failed: {'; '.join(messages or []) or resp.status_code}", code)
            return body
        raise ConnectorError("Jira is rate limiting requests. Try again in a minute.", "rate_limited")  # pragma: no cover

    def issue(self, key: str) -> dict[str, Any]:
        body = self.request("GET", f"/rest/api/3/issue/{key}", params={"fields": "summary,description,status,issuetype"})
        fields = body.get("fields") or {}
        return {"key": key, "summary": fields.get("summary", ""), "description": adf_to_text(fields.get("description")),
                "status": (fields.get("status") or {}).get("name", ""), "url": f"{self.token.get('site')}/browse/{key}"}

    def sync(self, store: Store, user_id: int) -> int:
        jql = "assignee = currentUser() OR reporter = currentUser() ORDER BY updated DESC"
        body = self.request("POST", "/rest/api/3/search/jql", json={
            "jql": jql, "maxResults": SYNC_LIMIT,
            "fields": ["summary", "description", "status", "issuetype", "labels", "resolution", "updated", "comment",
                       "assignee", "reporter"],
        })
        me = self.token.get("account_id", "")
        count = 0
        for issue in body.get("issues") or []:
            f = issue.get("fields") or {}
            mine = [adf_to_text(c.get("body")) for c in ((f.get("comment") or {}).get("comments") or [])
                    if (c.get("author") or {}).get("accountId") == me]
            count += bool(store.add_item(user_id, {
                "provider": "jira", "external_id": f"ticket:{issue.get('key')}", "kind": "ticket",
                "thread_id": f"jira:{issue.get('key')}",
                "direction": "outbound" if (f.get("assignee") or {}).get("accountId") == me else "inbound",
                "author_name": (f.get("reporter") or {}).get("displayName", ""),
                "subject": f"{issue.get('key')}: {f.get('summary', '')}"[:500],
                "body": adf_to_text(f.get("description")), "channel": issue.get("key", "").split("-")[0],
                "occurred_at": f.get("updated") or iso(),
                "meta": {"url": f"{self.token.get('site')}/browse/{issue.get('key')}",
                         "status": (f.get("status") or {}).get("name", ""),
                         "type": (f.get("issuetype") or {}).get("name", ""), "labels": f.get("labels") or [],
                         "resolved": bool(f.get("resolution")), "my_comments": mine[:10]},
            }))
        return count

    def create_issue(self, project: str, summary: str, description: str, issuetype: str = "Task") -> dict[str, Any]:
        out = self.request("POST", "/rest/api/3/issue", json={"fields": {
            "project": {"key": project}, "summary": summary, "description": text_to_adf(description),
            "issuetype": {"name": issuetype}}})
        key = out.get("key", "")
        return {"external_id": key, "url": f"{self.token.get('site')}/browse/{key}",
                "undo": {"provider": "jira", "op": "delete_issue", "key": key}}

    def comment(self, key: str, body: str) -> dict[str, Any]:
        out = self.request("POST", f"/rest/api/3/issue/{key}/comment", json={"body": text_to_adf(body)})
        return {"external_id": str(out.get("id", "")), "url": f"{self.token.get('site')}/browse/{key}",
                "undo": {"provider": "jira", "op": "delete_comment", "key": key, "id": out.get("id")}}

    def undo(self, info: dict[str, Any]) -> bool:
        if info.get("op") == "delete_comment":
            self.request("DELETE", f"/rest/api/3/issue/{info['key']}/comment/{info['id']}")
            return True
        if info.get("op") == "delete_issue":
            self.request("DELETE", f"/rest/api/3/issue/{info['key']}")
            return True
        return False
