"""
anote-sdk — Python SDK for the Anote AI assistant REST API.

Example::

    from anote_sdk import AnoteClient

    client = AnoteClient(api_key="<jwt-access-token>", base_url="http://localhost:5000")

    result = client.chat("Explain this codebase")
    print(result.response)
"""

from .client import AnoteClient, AsyncAnoteClient, AnoteError
from .models import (
    ChatMessage,
    ChatResult,
    SessionMessages,
    SearchResult,
    SearchResponse,
    HealthResult,
)

__all__ = [
    "AnoteClient",
    "AsyncAnoteClient",
    "AnoteError",
    "ChatMessage",
    "ChatResult",
    "SessionMessages",
    "SearchResult",
    "SearchResponse",
    "HealthResult",
]
__version__ = "1.0.0"
