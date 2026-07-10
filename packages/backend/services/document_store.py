"""Persistent document metadata storage.

Same dual-backend pattern as services.chat_sessions: ``DocumentStore``
(SQLite, zero-setup default) and ``MySQLDocumentStore`` (production, over the
existing ``documents`` table keyed by ``doc_uuid``). Select via the
``PERSISTENCE_BACKEND`` config through ``document_store_from_config``.
Documents may be owned by a user (``user_id``) or anonymous (NULL).
"""
from __future__ import annotations

import sqlite3
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def _now() -> int:
    return int(time.time())


def _iso(ts: int) -> str:
    return datetime.fromtimestamp(ts, tz=UTC).isoformat().replace("+00:00", "Z")


def _iso_dt(dt: datetime | None) -> str:
    if dt is None:
        return ""
    return dt.replace(microsecond=0).isoformat() + "Z"


def document_store_from_config(config: Any) -> DocumentStore | MySQLDocumentStore:
    """Build the document store selected by ``PERSISTENCE_BACKEND``."""
    if (config.get("PERSISTENCE_BACKEND") or "sqlite").lower() == "mysql":
        return MySQLDocumentStore()
    return DocumentStore(config["DOCUMENT_METADATA_DB_PATH"])


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
                    user_id INTEGER,
                    created_at INTEGER NOT NULL,
                    updated_at INTEGER NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_documents_updated
                    ON documents(updated_at);
                """
            )
            # Databases created before user scoping lack the user_id column.
            columns = {row["name"] for row in conn.execute("PRAGMA table_info(documents)")}
            if "user_id" not in columns:
                conn.execute("ALTER TABLE documents ADD COLUMN user_id INTEGER")

    def save_document(
        self,
        *,
        doc_id: str,
        filename: str,
        path: str | Path,
        chunks: int,
        content_type: str = "",
        user_id: int | None = None,
    ) -> dict:
        now = _now()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO documents
                    (id, filename, path, chunks, content_type, user_id, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
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
                    user_id,
                    now,
                    now,
                ),
            )
        document = self.get_document(doc_id)
        if document is None:
            raise RuntimeError("failed to save document metadata")
        return document

    def list_documents(self, user_id: int | None = None) -> list[dict]:
        where = "user_id = ?" if user_id is not None else "user_id IS NULL"
        params: tuple = (user_id,) if user_id is not None else ()
        with self._connect() as conn:
            rows = conn.execute(
                f"""
                SELECT id, filename, path, chunks, content_type, user_id, created_at, updated_at
                FROM documents
                WHERE {where}
                ORDER BY updated_at DESC
                """,
                params,
            ).fetchall()
        return [self._document_from_row(row) for row in rows]

    def get_document(self, doc_id: str) -> dict | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT id, filename, path, chunks, content_type, user_id, created_at, updated_at
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
            "userId": row["user_id"],
            "createdAt": _iso(created_at),
            "updatedAt": _iso(updated_at),
            "created_at": created_at,
            "updated_at": updated_at,
        }


class MySQLDocumentStore:
    """MySQL-backed document metadata store over the ``documents`` table.

    Documents are addressed by ``documents.doc_uuid`` so the public interface
    (UUID string ids) matches ``DocumentStore``.
    """

    _DOC_SELECT = (
        "SELECT id, doc_uuid, filename, path, chunk_count, content_type, user_id, "
        "created_at, updated_at FROM documents"
    )

    def _connect(self) -> Any:
        from database.db import get_connection

        return get_connection()

    def save_document(
        self,
        *,
        doc_id: str,
        filename: str,
        path: str | Path,
        chunks: int,
        content_type: str = "",
        user_id: int | None = None,
    ) -> dict:
        cnx = self._connect()
        try:
            cursor = cnx.cursor()
            cursor.execute(
                "INSERT INTO documents "
                "(user_id, doc_uuid, filename, path, chunk_count, content_type, created_at, updated_at) "
                "VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW()) "
                "ON DUPLICATE KEY UPDATE filename = VALUES(filename), path = VALUES(path), "
                "chunk_count = VALUES(chunk_count), content_type = VALUES(content_type), "
                "updated_at = NOW()",
                (user_id, doc_id, filename or "upload", str(path), int(chunks), content_type or ""),
            )
            cursor.close()
            document = self._get_by_uuid(cnx, doc_id)
            if document is None:
                raise RuntimeError("failed to save document metadata")
            return document
        finally:
            cnx.close()

    def list_documents(self, user_id: int | None = None) -> list[dict]:
        where = "WHERE user_id = %s" if user_id is not None else "WHERE user_id IS NULL"
        params: tuple = (user_id,) if user_id is not None else ()
        cnx = self._connect()
        try:
            cursor = cnx.cursor(dictionary=True)
            cursor.execute(f"{self._DOC_SELECT} {where} ORDER BY updated_at DESC", params)
            rows = cursor.fetchall()
            cursor.close()
            return [self._document_from_row(row) for row in rows]
        finally:
            cnx.close()

    def get_document(self, doc_id: str) -> dict | None:
        cnx = self._connect()
        try:
            return self._get_by_uuid(cnx, doc_id)
        finally:
            cnx.close()

    def delete_document(self, doc_id: str) -> dict | None:
        cnx = self._connect()
        try:
            document = self._get_by_uuid(cnx, doc_id)
            if document is None:
                return None
            cursor = cnx.cursor()
            cursor.execute("DELETE FROM documents WHERE doc_uuid = %s", (doc_id,))
            cursor.close()
            return document
        finally:
            cnx.close()

    def _get_by_uuid(self, cnx: Any, doc_id: str) -> dict | None:
        cursor = cnx.cursor(dictionary=True)
        cursor.execute(f"{self._DOC_SELECT} WHERE doc_uuid = %s", (doc_id,))
        row = cursor.fetchone()
        cursor.close()
        return self._document_from_row(row) if row else None

    @staticmethod
    def _document_from_row(row: dict) -> dict:
        created = row["created_at"]
        updated = row["updated_at"]
        return {
            "id": row["doc_uuid"],
            "filename": row["filename"],
            "path": row["path"] or "",
            "chunks": int(row["chunk_count"]),
            "contentType": row["content_type"] or "",
            "userId": row["user_id"],
            "createdAt": _iso_dt(created),
            "updatedAt": _iso_dt(updated),
            "created_at": int(created.timestamp()) if created else 0,
            "updated_at": int(updated.timestamp()) if updated else 0,
        }
