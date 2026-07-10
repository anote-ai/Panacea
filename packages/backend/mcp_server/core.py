"""Document Q&A engine behind the MCP server.

Self-contained pipeline: page-aware text extraction (PDF/txt/md/csv, local
path or URL), chunking into a dedicated Chroma collection, and a small SQLite
registry for document metadata and full text (used by summarize). Answering
reuses services.llm.complete, so any provider supported there works.

All state lives under ANOTE_MCP_DATA_DIR (default ~/.anote), so the server
works the same from any working directory.
"""
from __future__ import annotations

import os
import sqlite3
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from services.llm import complete

_TEXT_EXTS = {".txt", ".md", ".csv"}
_SUPPORTED_EXTS = _TEXT_EXTS | {".pdf"}
_CONTENT_TYPE_EXT = {
    "application/pdf": ".pdf",
    "text/plain": ".txt",
    "text/markdown": ".md",
    "text/csv": ".csv",
}
_MAX_SUMMARY_CHARS = 100_000


def _data_dir() -> Path:
    return Path(os.environ.get("ANOTE_MCP_DATA_DIR", str(Path.home() / ".anote"))).expanduser()


def _default_model() -> str:
    return os.environ.get("ANOTE_MCP_MODEL", "claude-sonnet-4-6")


def _connect() -> sqlite3.Connection:
    path = _data_dir() / "mcp_documents.sqlite3"
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            project TEXT NOT NULL,
            name TEXT NOT NULL,
            pages INTEGER NOT NULL,
            path TEXT NOT NULL DEFAULT '',
            text TEXT NOT NULL DEFAULT '',
            uploaded_at INTEGER NOT NULL
        )
        """
    )
    return conn


def _collection() -> Any:
    import chromadb
    from chromadb.utils import embedding_functions

    persist_dir = os.environ.get("CHROMA_PERSIST_DIR", str(_data_dir() / "chroma_db"))
    client = chromadb.PersistentClient(path=persist_dir)
    ef = embedding_functions.DefaultEmbeddingFunction()
    return client.get_or_create_collection(
        "mcp_documents", embedding_function=ef  # type: ignore[arg-type]
    )


def _iso(ts: int) -> str:
    return datetime.fromtimestamp(ts, tz=UTC).isoformat().replace("+00:00", "Z")


def _extract_pages(path: Path) -> list[str]:
    """Return the document's text, one string per page (non-PDFs are 1 page)."""
    ext = path.suffix.lower()
    if ext in _TEXT_EXTS:
        return [path.read_text(encoding="utf-8", errors="ignore")]
    if ext == ".pdf":
        import PyPDF2

        with open(path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            return [page.extract_text() or "" for page in reader.pages]
    raise ValueError(f"unsupported file type: {ext or path.name} (supported: pdf, txt, md, csv)")


def _chunk(text: str, chunk_size: int = 1000, overlap: int = 100) -> list[str]:
    if not text.strip():
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks


def _fetch_url(url: str) -> Path:
    """Download a document to the local data dir and return its path."""
    import requests  # type: ignore[import-untyped]

    response = requests.get(url, timeout=60)
    response.raise_for_status()

    ext = Path(urlparse(url).path).suffix.lower()
    if ext not in _SUPPORTED_EXTS:
        content_type = (response.headers.get("Content-Type") or "").split(";")[0].strip().lower()
        ext = _CONTENT_TYPE_EXT.get(content_type, "")
    if ext not in _SUPPORTED_EXTS:
        raise ValueError(f"could not determine a supported file type for URL: {url}")

    downloads = _data_dir() / "downloads"
    downloads.mkdir(parents=True, exist_ok=True)
    path = downloads / f"{uuid.uuid4()}{ext}"
    path.write_bytes(response.content)
    return path


def upload_document(file_path: str, project_name: str) -> dict:
    """Extract, chunk, and index a document (local path or URL) into a project."""
    if not project_name.strip():
        raise ValueError("project_name is required")

    source = str(file_path).strip()
    if source.startswith(("http://", "https://")):
        path = _fetch_url(source)
        name = Path(urlparse(source).path).name or path.name
    else:
        path = Path(source).expanduser().resolve()
        if not path.is_file():
            raise ValueError(f"file not found: {source}")
        name = path.name

    pages = _extract_pages(path)
    doc_id = str(uuid.uuid4())

    chunk_texts: list[str] = []
    chunk_ids: list[str] = []
    chunk_metas: list[dict] = []
    for page_number, page_text in enumerate(pages, start=1):
        for i, chunk in enumerate(_chunk(page_text)):
            chunk_texts.append(chunk)
            chunk_ids.append(f"{doc_id}-p{page_number}-c{i}")
            chunk_metas.append(
                {"document_id": doc_id, "project": project_name, "page": page_number}
            )
    if chunk_texts:
        _collection().add(documents=chunk_texts, ids=chunk_ids, metadatas=chunk_metas)

    with _connect() as conn:
        conn.execute(
            "INSERT INTO documents (id, project, name, pages, path, text, uploaded_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                doc_id,
                project_name,
                name,
                len(pages),
                str(path),
                "\n\n".join(pages),
                int(time.time()),
            ),
        )

    return {"document_id": doc_id, "pages": len(pages), "status": "indexed"}


def list_documents(project_id: str) -> list[dict]:
    """List the documents indexed in a project."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT id, name, pages, uploaded_at FROM documents "
            "WHERE project = ? ORDER BY uploaded_at DESC",
            (project_id,),
        ).fetchall()
    return [
        {
            "id": row["id"],
            "name": row["name"],
            "pages": int(row["pages"]),
            "uploaded_at": _iso(int(row["uploaded_at"])),
        }
        for row in rows
    ]


def ask_question(
    question: str,
    document_id: str | None = None,
    project_id: str | None = None,
    top_k: int = 5,
) -> dict:
    """Answer a question from one document or a whole project, with sources."""
    if not question.strip():
        raise ValueError("question is required")
    if not document_id and not project_id:
        raise ValueError("either document_id or project_id is required")

    where: dict = (
        {"document_id": document_id} if document_id else {"project": project_id}
    )
    results = _collection().query(
        query_texts=[question],
        n_results=max(1, top_k),
        where=where,
        include=["documents", "metadatas", "distances"],
    )
    docs = (results.get("documents") or [[]])[0]
    metas = (results.get("metadatas") or [[]])[0]
    distances = (results.get("distances") or [[]])[0]

    sources = [
        {
            "chunk": chunk,
            "page": int((meta or {}).get("page", 0)),
            "score": round(1.0 / (1.0 + max(0.0, distance)), 4),
        }
        for chunk, meta, distance in zip(docs, metas, distances)
    ]
    if not sources:
        return {
            "answer": "No relevant content found in the selected documents.",
            "confidence": 0.0,
            "sources": [],
        }

    context = "\n\n---\n\n".join(
        f"[page {source['page']}]\n{source['chunk']}" for source in sources
    )
    if os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("OPENAI_API_KEY"):
        answer = complete(
            f"Answer the question using only the context below. "
            f"If the context is insufficient, say so.\n\n"
            f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer:",
            model=_default_model(),
        )
    else:
        answer = f"(no LLM API key configured) Most relevant context:\n{context[:1000]}"

    return {
        "answer": answer,
        "confidence": max(source["score"] for source in sources),
        "sources": sources,
    }


def summarize_document(document_id: str, focus: str | None = None) -> dict:
    """Summarize an indexed document, optionally focused on a topic."""
    with _connect() as conn:
        row = conn.execute(
            "SELECT name, text FROM documents WHERE id = ?", (document_id,)
        ).fetchone()
    if row is None:
        raise ValueError(f"unknown document: {document_id}")

    text = row["text"][:_MAX_SUMMARY_CHARS]
    if not (os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("OPENAI_API_KEY")):
        return {"summary": f"(no LLM API key configured) Document preview:\n{text[:1000]}"}

    focus_line = f" Focus on: {focus}." if focus else ""
    summary = complete(
        f"Summarize the following document ({row['name']}).{focus_line}\n\n{text}",
        model=_default_model(),
    )
    return {"summary": summary}
