"""Pydantic v2 models for Anote API responses (camelCase JSON → snake_case Python)."""

from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, ConfigDict


def _camel(s: str) -> str:
    parts = s.split("_")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


class _Base(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=_camel)


class ChatMessage(_Base):
    role: Literal["user", "assistant"]
    content: str


class ChatResult(_Base):
    response: str
    model: str


class SessionMessages(_Base):
    session_id: str
    messages: list[ChatMessage] = []


class SearchResult(_Base):
    file: str = ""
    start_line: int = 0
    end_line: int = 0
    preview: str = ""
    score: float = 0.0


class SearchResponse(_Base):
    results: list[SearchResult] = []
    query: str = ""
    cwd: str = ""


class HealthResult(_Base):
    status: str = "ok"
    service: str = ""
