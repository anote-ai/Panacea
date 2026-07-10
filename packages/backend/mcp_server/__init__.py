"""Anote document Q&A — MCP server and importable Python API (issue #206).

Clean Python API (usable without MCP, e.g. by anote-mcp-server):

    from mcp_server import upload_document, list_documents, ask_question, summarize_document

Run as an MCP server (stdio) from packages/backend:

    python -m mcp_server.server
"""
from mcp_server.core import (
    ask_question,
    list_documents,
    summarize_document,
    upload_document,
)

__all__ = ["upload_document", "list_documents", "ask_question", "summarize_document"]
