"""MCP servers: plug any Model Context Protocol server into the coworker.

Uses the Streamable HTTP transport (JSON-RPC over POST; responses come back as
JSON or as a short server-sent-event stream). Connecting runs ``initialize`` and
``tools/list``; calling a tool is an ``mcp.call`` action, so it goes through the
same approvals and autonomy rules as an email.

Servers must be ``https://`` and resolve to public addresses, so a pasted URL
can't be used to reach this server's internal network. Set
``COWORKER_MCP_ALLOW_PRIVATE=1`` for local development.
"""
from __future__ import annotations

import ipaddress
import json
import os
import re
import socket
from typing import Any
from urllib.parse import urlparse

import requests

from coworker.connectors.base import ConnectorError

PROTOCOL_VERSION = "2025-06-18"
TIMEOUT = 30
PREFIX = "mcp_"


def slug(name: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:30]
    if not value:
        raise ConnectorError("Give the server a name", "bad_request")
    return value


def provider_for(name: str) -> str:
    return f"{PREFIX}{slug(name)}"


def is_mcp(provider: str) -> bool:
    return provider.startswith(PREFIX)


def check_url(url: str) -> str:
    """Reject URLs that would let a user point the server at itself or its private network."""
    parsed = urlparse(url.strip())
    allow_private = os.environ.get("COWORKER_MCP_ALLOW_PRIVATE") == "1"
    if parsed.scheme != "https" and not (allow_private and parsed.scheme == "http"):
        raise ConnectorError("MCP servers must use https://", "bad_request")
    if not parsed.hostname:
        raise ConnectorError("That isn't a URL", "bad_request")
    if not allow_private:
        try:
            infos = socket.getaddrinfo(parsed.hostname, parsed.port or 443, proto=socket.IPPROTO_TCP)
        except socket.gaierror as exc:
            raise ConnectorError(f"Can't resolve {parsed.hostname}", "bad_request") from exc
        for info in infos:
            ip = ipaddress.ip_address(info[4][0])
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
                raise ConnectorError("MCP servers must be on the public internet", "bad_request")
    return url.strip()


def _parse(resp: requests.Response) -> dict[str, Any]:
    kind = resp.headers.get("Content-Type", "")
    if "text/event-stream" in kind:
        last: dict[str, Any] = {}
        for line in resp.text.splitlines():
            if line.startswith("data:"):
                try:
                    msg = json.loads(line[5:].strip())
                except ValueError:
                    continue
                if "result" in msg or "error" in msg:
                    last = msg
        return last
    return resp.json() if resp.content else {}


class MCPClient:
    label = "MCP"

    def __init__(self, token: dict[str, Any], on_refresh: Any = None) -> None:
        self.token = token
        self.url = str(token.get("url", ""))
        self.session = str(token.get("session", ""))
        self._id = 0

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream",
                   "MCP-Protocol-Version": PROTOCOL_VERSION}
        if self.token.get("auth"):
            headers["Authorization"] = f"Bearer {self.token['auth']}"
        if self.session:
            headers["Mcp-Session-Id"] = self.session
        return headers

    def rpc(self, method: str, params: dict[str, Any] | None = None, notify: bool = False) -> dict[str, Any]:
        self._id += 1
        body: dict[str, Any] = {"jsonrpc": "2.0", "method": method, "params": params or {}}
        if not notify:
            body["id"] = self._id
        try:
            resp = requests.post(check_url(self.url), json=body, headers=self._headers(), timeout=TIMEOUT)
        except requests.RequestException as exc:
            raise ConnectorError(f"Couldn't reach the MCP server: {exc}", "provider_error") from exc
        if resp.headers.get("Mcp-Session-Id"):
            self.session = resp.headers["Mcp-Session-Id"]
        if resp.status_code in (401, 403):
            raise ConnectorError("The MCP server refused the credentials", "reauth_required")
        if resp.status_code >= 400:
            raise ConnectorError(f"The MCP server returned {resp.status_code}", "provider_error")
        if notify:
            return {}
        msg = _parse(resp)
        if msg.get("error"):
            raise ConnectorError(f"MCP {method} failed: {msg['error'].get('message', '')}", "provider_error")
        result: dict[str, Any] = msg.get("result") or {}
        return result

    def initialize(self) -> dict[str, Any]:
        info = self.rpc("initialize", {"protocolVersion": PROTOCOL_VERSION, "capabilities": {},
                                       "clientInfo": {"name": "ourogen-coworker", "version": "1"}})
        self.rpc("notifications/initialized", notify=True)
        return info

    def list_tools(self) -> list[dict[str, Any]]:
        self.initialize()
        tools = self.rpc("tools/list").get("tools") or []
        return [{"name": t.get("name", ""), "description": (t.get("description") or "")[:500],
                 "inputSchema": t.get("inputSchema") or {}} for t in tools]

    def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        self.initialize()
        result = self.rpc("tools/call", {"name": name, "arguments": arguments})
        text = "\n".join(c.get("text", "") for c in result.get("content") or [] if c.get("type") == "text")
        return {"text": text[:20000], "isError": bool(result.get("isError"))}


def connect(name: str, url: str, auth: str = "") -> dict[str, Any]:
    """Verify a server and return the token to store: its URL, credentials and tools."""
    token: dict[str, Any] = {"kind": "mcp", "name": name.strip()[:80], "url": check_url(url), "auth": auth.strip()}
    client = MCPClient(token)
    info = client.initialize()
    token["server"] = ((info.get("serverInfo") or {}).get("name")) or name
    token["tools"] = client.list_tools()
    return token
