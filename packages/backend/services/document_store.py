"""Persistent document metadata storage backed by SQLite."""
from __future__ import annotations

import sqlite3
import time
from datetime import UTC, datetime
from pathlib import Path


def _now() -> int:
    return int(time.time())


def _iso(ts: int) -> str:
    return datetime.fromtimestamp(ts, tz=UTC).isoformat().replace("+00:00", "Z")


class DocumentStore:
    """Small SQLite store for uploaded document metadata."""

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    path TEXT NOT NULL,
                    chunks INTEGER NOT NULL DEFAULT 0,
                    content_type TEXT NOT NULL DEFAULT '',
                    created_at INTEGER NOT NULL,
                    updated_at INTEGER NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_documents_updated
                    ON documents(updated_at);
                """
            )

    def save_document(
        self,
        *,
        doc_id: str,
        filename: str,
        path: str | Path,
        chunks: int,
        content_type: str = "",
    ) -> dict:
        now = _now()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO documents
                    (id, filename, path, chunks, content_type, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    filename = excluded.filename,
                    path = excluded.path,
                    chunks = excluded.chunks,
                    content_type = excluded.content_type,
                    updated_at = excluded.updated_at
                """,
                (
                    doc_id,
                    filename or "upload",
                    str(path),
                    int(chunks),
                    content_type or "",
                    now,
                    now,
                ),
            )
        document = self.get_document(doc_id)
        if document is None:
            raise RuntimeError("failed to save document metadata")
        return document

    def list_documents(self) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, filename, path, chunks, content_type, created_at, updated_at
                FROM documents
                ORDER BY updated_at DESC
                """
            ).fetchall()
        return [self._document_from_row(row) for row in rows]

    def get_document(self, doc_id: str) -> dict | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT id, filename, path, chunks, content_type, created_at, updated_at
                FROM documents
                WHERE id = ?
                """,
                (doc_id,),
            ).fetchone()
        return self._document_from_row(row) if row else None

    def delete_document(self, doc_id: str) -> dict | None:
        document = self.get_document(doc_id)
        if document is None:
            return None
        with self._connect() as conn:
            conn.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        return document

    @staticmethod
    def _document_from_row(row: sqlite3.Row) -> dict:
        created_at = int(row["created_at"])
        updated_at = int(row["updated_at"])
        return {
            "id": row["id"],
            "filename": row["filename"],
            "path": row["path"],
            "chunks": int(row["chunks"]),
            "contentType": row["content_type"],
            "createdAt": _iso(created_at),
            "updatedAt": _iso(updated_at),
            "created_at": created_at,
            "updated_at": updated_at,
        }
