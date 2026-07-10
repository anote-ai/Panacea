"""MCP server exposing document Q&A tools over stdio (issue #206).

Run from packages/backend:

    python -m mcp_server.server
"""
from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from mcp_server import core

mcp = FastMCP("anote-doc-qa")


@mcp.tool()
def upload_document(file_path: str, project_name: str) -> dict:
    """Index a document (local path or URL; pdf/txt/md/csv) into a named project.

    Returns {"document_id", "pages", "status"}. Use the document_id with
    ask_question and summarize_document, or the project_name to search across
    every document in the project.
    """
    return core.upload_document(file_path=file_path, project_name=project_name)


@mcp.tool()
def list_documents(project_id: str) -> list[dict]:
    """List indexed documents in a project: id, name, pages, uploaded_at."""
    return core.list_documents(project_id=project_id)


@mcp.tool()
def ask_question(
    question: str, document_id: str = "", project_id: str = "", top_k: int = 5
) -> dict:
    """Answer a question from one document (document_id) or a project (project_id).

    Returns {"answer", "confidence", "sources": [{"chunk", "page", "score"}]}.
    top_k controls how many chunks are retrieved as context.
    """
    return core.ask_question(
        question=question,
        document_id=document_id or None,
        project_id=project_id or None,
        top_k=top_k,
    )


@mcp.tool()
def summarize_document(document_id: str, focus: str = "") -> dict:
    """Summarize an indexed document; optional focus (e.g. "key risks")."""
    return core.summarize_document(document_id=document_id, focus=focus or None)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
