"""Persistent chat session storage backed by SQLite."""
from __future__ import annotations

import sqlite3
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

MessageRole = Literal["user", "assistant", "system"]


def _now() -> int:
    return int(time.time())


def _iso(ts: int) -> str:
    return datetime.fromtimestamp(ts, tz=UTC).isoformat().replace("+00:00", "Z")


class ChatSessionStore:
    """Small SQLite-backed store for chat sessions and messages."""

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    session_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL DEFAULT 'New chat',
                    cwd TEXT NOT NULL DEFAULT '',
                    model TEXT NOT NULL DEFAULT '',
                    created_at INTEGER NOT NULL,
                    updated_at INTEGER NOT NULL
                );

                CREATE TABLE IF NOT EXISTS chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
                    content TEXT NOT NULL,
                    model TEXT NOT NULL DEFAULT '',
                    created_at INTEGER NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_chat_messages_session_created
                    ON chat_messages(session_id, created_at, id);
                CREATE INDEX IF NOT EXISTS idx_chat_sessions_updated
                    ON chat_sessions(updated_at);
                """
            )

    def create_session(
        self,
        *,
        session_id: str | None = None,
        title: str = "New chat",
        cwd: str = "",
        model: str = "",
    ) -> dict:
        sid = session_id or str(uuid.uuid4())
        now = _now()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR IGNORE INTO chat_sessions
                    (session_id, title, cwd, model, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (sid, title or "New chat", cwd or "", model or "", now, now),
            )
        session = self.get_session(sid)
        if session is None:
            raise RuntimeError("failed to create chat session")
        return session

    def ensure_session(
        self,
        session_id: str | None,
        *,
        title: str = "New chat",
        cwd: str = "",
        model: str = "",
    ) -> dict:
        if session_id:
            existing = self.get_session(session_id)
            if existing:
                return existing
        return self.create_session(session_id=session_id, title=title, cwd=cwd, model=model)

    def list_sessions(self) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT
                    s.session_id,
                    s.title,
                    s.cwd,
                    s.model,
                    s.created_at,
                    s.updated_at,
                    COUNT(m.id) AS message_count
                FROM chat_sessions s
                LEFT JOIN chat_messages m ON m.session_id = s.session_id
                GROUP BY s.session_id
                ORDER BY s.updated_at DESC
                """
            ).fetchall()
        return [self._session_from_row(row) for row in rows]

    def get_session(self, session_id: str) -> dict | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT
                    s.session_id,
                    s.title,
                    s.cwd,
                    s.model,
                    s.created_at,
                    s.updated_at,
                    COUNT(m.id) AS message_count
                FROM chat_sessions s
                LEFT JOIN chat_messages m ON m.session_id = s.session_id
                WHERE s.session_id = ?
                GROUP BY s.session_id
                """,
                (session_id,),
            ).fetchone()
        return self._session_from_row(row) if row else None

    def add_message(
        self,
        session_id: str,
        *,
        role: MessageRole,
        content: str,
        model: str = "",
    ) -> dict:
        if role not in {"user", "assistant", "system"}:
            raise ValueError(f"unsupported message role: {role}")

        now = _now()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO chat_messages (session_id, role, content, model, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (session_id, role, content, model or "", now),
            )
            if role == "user":
                conn.execute(
                    """
                    UPDATE chat_sessions
                    SET
                        title = CASE
                            WHEN title = 'New chat' THEN ?
                            ELSE title
                        END,
                        model = CASE
                            WHEN ? != '' THEN ?
                            ELSE model
                        END,
                        updated_at = ?
                    WHERE session_id = ?
                    """,
                    (self._title_from_message(content), model or "", model or "", now, session_id),
                )
            else:
                conn.execute(
                    """
                    UPDATE chat_sessions
                    SET
                        model = CASE
                            WHEN ? != '' THEN ?
                            ELSE model
                        END,
                        updated_at = ?
                    WHERE session_id = ?
                    """,
                    (model or "", model or "", now, session_id),
                )
            row = conn.execute("SELECT last_insert_rowid() AS id").fetchone()
        return {
            "id": str(row["id"]),
            "role": role,
            "content": content,
            "model": model,
            "createdAt": _iso(now),
            "ts": now,
        }

    def get_messages(self, session_id: str) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, role, content, model, created_at
                FROM chat_messages
                WHERE session_id = ?
                ORDER BY created_at ASC, id ASC
                """,
                (session_id,),
            ).fetchall()
        return [
            {
                "id": str(row["id"]),
                "role": row["role"],
                "content": row["content"],
                "model": row["model"],
                "createdAt": _iso(int(row["created_at"])),
                "ts": int(row["created_at"]),
            }
            for row in rows
        ]

    def delete_session(self, session_id: str) -> bool:
        with self._connect() as conn:
            cursor = conn.execute("DELETE FROM chat_sessions WHERE session_id = ?", (session_id,))
        return cursor.rowcount > 0

    @staticmethod
    def _title_from_message(content: str) -> str:
        first_line = " ".join(content.strip().splitlines()[0:1]).strip()
        if not first_line:
            return "New chat"
        return first_line[:77] + "..." if len(first_line) > 80 else first_line

    @staticmethod
    def _session_from_row(row: sqlite3.Row) -> dict:
        created_at = int(row["created_at"])
        updated_at = int(row["updated_at"])
        return {
            "id": row["session_id"],
            "sessionId": row["session_id"],
            "title": row["title"],
            "cwd": row["cwd"],
            "model": row["model"],
            "messageCount": int(row["message_count"]),
            "createdAt": _iso(created_at),
            "updatedAt": _iso(updated_at),
            "created_at": created_at,
            "updated_at": updated_at,
        }
