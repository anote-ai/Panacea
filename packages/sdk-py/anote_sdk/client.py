"""Anote API client — synchronous and async."""

from __future__ import annotations

from typing import Any, AsyncGenerator, Generator, Optional
import json
import httpx

from .models import (
    ChatMessage,
    ChatResult,
    SessionMessages,
    SearchResponse,
    HealthResult,
)


class AnoteError(Exception):
    """Raised when the Anote API returns a non-2xx response."""

    def __init__(self, message: str, status: int, body: Any) -> None:
        super().__init__(message)
        self.status = status
        self.body = body


def _raise_for_status(response: httpx.Response) -> dict:
    data: dict = {}
    try:
        data = response.json()
    except Exception:
        pass
    if response.is_error:
        msg = data.get("error") or f"HTTP {response.status_code}"
        raise AnoteError(msg, response.status_code, data)
    return data


def _parse_sse_events(raw: str) -> Generator[tuple[str, dict], None, None]:
    for event in raw.split("\n\n"):
        if not event.strip():
            continue
        event_type = "text"
        data = None
        for line in event.split("\n"):
            if line.startswith("event: "):
                event_type = line[len("event: "):]
            elif line.startswith("data: "):
                data = json.loads(line[len("data: "):])
        if data is not None:
            yield event_type, data


_DEFAULT_BASE = "https://api.anote.ai"
_USER_AGENT = "anote-sdk-python/1.0.0"


class AnoteClient:
    """Synchronous Anote API client.

    Args:
        api_key: Bearer token (JWT access token from ``/auth/login``).
        base_url: Server base URL. Defaults to ``https://api.anote.ai``.
        timeout: Request timeout in seconds. Defaults to 60.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = _DEFAULT_BASE,
        timeout: float = 60.0,
    ) -> None:
        if not api_key:
            raise ValueError("api_key is required")
        self._base = base_url.rstrip("/")
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "User-Agent": _USER_AGENT,
        }
        self._timeout = timeout

    def _get(self, path: str, params: Optional[dict] = None) -> dict:
        with httpx.Client(timeout=self._timeout) as http:
            r = http.get(f"{self._base}{path}", headers=self._headers, params=params)
            return _raise_for_status(r)

    def _post(self, path: str, body: Optional[dict] = None) -> dict:
        with httpx.Client(timeout=self._timeout) as http:
            r = http.post(f"{self._base}{path}", headers=self._headers, json=body or {})
            return _raise_for_status(r)

    def _delete(self, path: str) -> dict:
        with httpx.Client(timeout=self._timeout) as http:
            r = http.delete(f"{self._base}{path}", headers=self._headers)
            return _raise_for_status(r)

    def chat(
        self,
        message: str,
        *,
        model: str = "claude-sonnet-4-6",
        history: Optional[list[ChatMessage]] = None,
    ) -> ChatResult:
        """Send a message and receive a complete (non-streaming) AI response."""
        payload: dict = {"message": message, "model": model}
        if history:
            payload["history"] = [h.model_dump(by_alias=True) for h in history]
        return ChatResult.model_validate(self._post("/api/chat", payload))

    def chat_stream(
        self,
        message: str,
        *,
        model: str = "claude-sonnet-4-6",
        cwd: Optional[str] = None,
    ) -> Generator[str, None, None]:
        """Send a message and yield text chunks as they're generated over SSE."""
        payload: dict = {"message": message, "model": model}
        if cwd:
            payload["cwd"] = cwd
        with httpx.Client(timeout=self._timeout) as http:
            with http.stream(
                "POST", f"{self._base}/api/chat/stream", headers=self._headers, json=payload
            ) as r:
                if r.is_error:
                    r.read()
                    _raise_for_status(r)
                buffer = ""
                for chunk in r.iter_text():
                    buffer += chunk
                    while "\n\n" in buffer:
                        event, buffer = buffer.split("\n\n", 1)
                        for event_type, data in _parse_sse_events(event + "\n\n"):
                            if event_type == "text" and data.get("text"):
                                yield data["text"]
                            elif event_type == "error":
                                raise AnoteError(data.get("message", "stream error"), 0, data)

    # ── Sessions ──────────────────────────────────────────────────────────────
    # Note: sessions are currently just server-side placeholders — creating
    # one doesn't yet link it to chat()/chat_stream() calls.

    def create_session(self) -> str:
        """Create a new (empty) chat session. Returns the new session ID."""
        return self._post("/api/chat/sessions")["sessionId"]

    def list_sessions(self) -> list[str]:
        """List all chat session IDs on the server."""
        return self._get("/api/chat/sessions").get("sessions", [])

    def get_session_messages(self, session_id: str) -> SessionMessages:
        """Get the message history of a session."""
        return SessionMessages.model_validate(self._get(f"/api/chat/sessions/{session_id}"))

    def delete_session(self, session_id: str) -> bool:
        """Delete a session. Returns True on success."""
        return bool(self._delete(f"/api/chat/sessions/{session_id}").get("deleted"))

    # ── Search ────────────────────────────────────────────────────────────────

    def search(self, query: str, cwd: Optional[str] = None, top: int = 10) -> SearchResponse:
        """TF-IDF search over the codebase index built by `anote index`."""
        params: dict = {"q": query, "top": top}
        if cwd:
            params["cwd"] = cwd
        return SearchResponse.model_validate(self._get("/api/search", params=params))

    def health(self) -> HealthResult:
        """Check server liveness. Does not require authentication."""
        with httpx.Client(timeout=self._timeout) as http:
            r = http.get(f"{self._base}/health", headers={"User-Agent": _USER_AGENT})
            return HealthResult.model_validate(r.json())


class AsyncAnoteClient:
    """Async Anote API client for use with asyncio / anyio."""

    def __init__(
        self,
        api_key: str,
        base_url: str = _DEFAULT_BASE,
        timeout: float = 60.0,
    ) -> None:
        if not api_key:
            raise ValueError("api_key is required")
        self._base = base_url.rstrip("/")
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "User-Agent": _USER_AGENT,
        }
        self._timeout = timeout
        self._http: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "AsyncAnoteClient":
        self._http = httpx.AsyncClient(timeout=self._timeout)
        return self

    async def __aexit__(self, *_: Any) -> None:
        if self._http:
            await self._http.aclose()

    def _client(self) -> httpx.AsyncClient:
        if not self._http:
            raise RuntimeError("Use 'async with AsyncAnoteClient(...) as client'")
        return self._http

    async def _get(self, path: str, params: Optional[dict] = None) -> dict:
        r = await self._client().get(f"{self._base}{path}", headers=self._headers, params=params)
        return _raise_for_status(r)

    async def _post(self, path: str, body: Optional[dict] = None) -> dict:
        r = await self._client().post(f"{self._base}{path}", headers=self._headers, json=body or {})
        return _raise_for_status(r)

    async def _delete(self, path: str) -> dict:
        r = await self._client().delete(f"{self._base}{path}", headers=self._headers)
        return _raise_for_status(r)

    async def chat(
        self,
        message: str,
        *,
        model: str = "claude-sonnet-4-6",
        history: Optional[list[ChatMessage]] = None,
    ) -> ChatResult:
        payload: dict = {"message": message, "model": model}
        if history:
            payload["history"] = [h.model_dump(by_alias=True) for h in history]
        return ChatResult.model_validate(await self._post("/api/chat", payload))

    async def chat_stream(
        self,
        message: str,
        *,
        model: str = "claude-sonnet-4-6",
        cwd: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        payload: dict = {"message": message, "model": model}
        if cwd:
            payload["cwd"] = cwd
        async with self._client().stream(
            "POST", f"{self._base}/api/chat/stream", headers=self._headers, json=payload
        ) as r:
            if r.is_error:
                await r.aread()
                _raise_for_status(r)
            buffer = ""
            async for chunk in r.aiter_text():
                buffer += chunk
                while "\n\n" in buffer:
                    event, buffer = buffer.split("\n\n", 1)
                    for event_type, data in _parse_sse_events(event + "\n\n"):
                        if event_type == "text" and data.get("text"):
                            yield data["text"]
                        elif event_type == "error":
                            raise AnoteError(data.get("message", "stream error"), 0, data)

    async def create_session(self) -> str:
        return (await self._post("/api/chat/sessions"))["sessionId"]

    async def list_sessions(self) -> list[str]:
        return (await self._get("/api/chat/sessions")).get("sessions", [])

    async def get_session_messages(self, session_id: str) -> SessionMessages:
        return SessionMessages.model_validate(await self._get(f"/api/chat/sessions/{session_id}"))

    async def delete_session(self, session_id: str) -> bool:
        return bool((await self._delete(f"/api/chat/sessions/{session_id}")).get("deleted"))

    async def search(self, query: str, cwd: Optional[str] = None, top: int = 10) -> SearchResponse:
        params: dict = {"q": query, "top": top}
        if cwd:
            params["cwd"] = cwd
        return SearchResponse.model_validate(await self._get("/api/search", params=params))

    async def health(self) -> HealthResult:
        r = await self._client().get(f"{self._base}/health", headers={"User-Agent": _USER_AGENT})
        return HealthResult.model_validate(r.json())
