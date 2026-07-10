"""Persistent chat session storage.

Two interchangeable backends behind the same interface:

- ``ChatSessionStore`` — SQLite, zero-setup default for local dev and CI.
- ``MySQLChatSessionStore`` — MySQL, user-scoped, for production where the
  ``chats``/``messages`` tables already exist (see database/schema.sql).

Select via the ``PERSISTENCE_BACKEND`` config ("sqlite" | "mysql") through
``chat_store_from_config``. Sessions may be owned by a user (``user_id``) or
anonymous (``user_id`` NULL); ownership checks live in the HTTP handlers.
"""
from __future__ import annotations

import sqlite3
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

MessageRole = Literal["user", "assistant", "system"]

_DEFAULT_TITLES = ("New chat", "New Chat")


def _now() -> int:
    return int(time.time())


def _iso(ts: int) -> str:
    return datetime.fromtimestamp(ts, tz=UTC).isoformat().replace("+00:00", "Z")


def _iso_dt(dt: datetime | None) -> str:
    if dt is None:
        return ""
    return dt.replace(microsecond=0).isoformat() + "Z"


def _title_from_message(content: str) -> str:
    first_line = " ".join(content.strip().splitlines()[0:1]).strip()
    if not first_line:
        return "New chat"
    return first_line[:77] + "..." if len(first_line) > 80 else first_line


def chat_store_from_config(config: Any) -> ChatSessionStore | MySQLChatSessionStore:
    """Build the chat store selected by ``PERSISTENCE_BACKEND``."""
    if (config.get("PERSISTENCE_BACKEND") or "sqlite").lower() == "mysql":
        return MySQLChatSessionStore()
    return ChatSessionStore(config["CHAT_SESSION_DB_PATH"])


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
                    user_id INTEGER,
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
            # Databases created before user scoping lack the user_id column.
            columns = {row["name"] for row in conn.execute("PRAGMA table_info(chat_sessions)")}
            if "user_id" not in columns:
                conn.execute("ALTER TABLE chat_sessions ADD COLUMN user_id INTEGER")

    def create_session(
        self,
        *,
        session_id: str | None = None,
        title: str = "New chat",
        cwd: str = "",
        model: str = "",
        user_id: int | None = None,
    ) -> dict:
        sid = session_id or str(uuid.uuid4())
        now = _now()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR IGNORE INTO chat_sessions
                    (session_id, title, cwd, model, user_id, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (sid, title or "New chat", cwd or "", model or "", user_id, now, now),
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
        user_id: int | None = None,
    ) -> dict:
        if session_id:
            existing = self.get_session(session_id)
            if existing:
                return existing
        return self.create_session(
            session_id=session_id, title=title, cwd=cwd, model=model, user_id=user_id
        )

    def list_sessions(self, user_id: int | None = None) -> list[dict]:
        where = "s.user_id = ?" if user_id is not None else "s.user_id IS NULL"
        params: tuple = (user_id,) if user_id is not None else ()
        with self._connect() as conn:
            rows = conn.execute(
                f"""
                SELECT
                    s.session_id,
                    s.title,
                    s.cwd,
                    s.model,
                    s.user_id,
                    s.created_at,
                    s.updated_at,
                    COUNT(m.id) AS message_count
                FROM chat_sessions s
                LEFT JOIN chat_messages m ON m.session_id = s.session_id
                WHERE {where}
                GROUP BY s.session_id
                ORDER BY s.updated_at DESC
                """,
                params,
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
                    s.user_id,
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
                            WHEN title IN ('New chat', 'New Chat') THEN ?
                            ELSE title
                        END,
                        model = CASE
                            WHEN ? != '' THEN ?
                            ELSE model
                        END,
                        updated_at = ?
                    WHERE session_id = ?
                    """,
                    (_title_from_message(content), model or "", model or "", now, session_id),
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
    def _session_from_row(row: sqlite3.Row) -> dict:
        created_at = int(row["created_at"])
        updated_at = int(row["updated_at"])
        return {
            "id": row["session_id"],
            "sessionId": row["session_id"],
            "title": row["title"],
            "cwd": row["cwd"],
            "model": row["model"],
            "userId": row["user_id"],
            "messageCount": int(row["message_count"]),
            "createdAt": _iso(created_at),
            "updatedAt": _iso(updated_at),
            "created_at": created_at,
            "updated_at": updated_at,
        }


class MySQLChatSessionStore:
    """MySQL-backed chat store over the existing ``chats``/``messages`` tables.

    Sessions are addressed by ``chats.session_uuid`` so the public interface
    (UUID string ids) matches ``ChatSessionStore``; the integer primary key
    stays internal. Supersedes the helper layer from PR #252.
    """

    _SESSION_SELECT = """
        SELECT
            c.id,
            c.session_uuid,
            c.name,
            c.cwd,
            c.model,
            c.user_id,
            c.created_at,
            c.updated_at,
            (SELECT COUNT(*) FROM messages m WHERE m.chat_id = c.id) AS message_count
        FROM chats c
    """

    def _connect(self) -> Any:
        from database.db import get_connection

        return get_connection()

    def create_session(
        self,
        *,
        session_id: str | None = None,
        title: str = "New chat",
        cwd: str = "",
        model: str = "",
        user_id: int | None = None,
    ) -> dict:
        sid = session_id or str(uuid.uuid4())
        cnx = self._connect()
        try:
            existing = self._get_by_uuid(cnx, sid)
            if existing:
                return existing
            cursor = cnx.cursor()
            cursor.execute(
                "INSERT INTO chats (user_id, name, mode, session_uuid, cwd, model, created_at, updated_at) "
                "VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())",
                (user_id, title or "New chat", "chat", sid, cwd or "", model or ""),
            )
            cursor.close()
            session = self._get_by_uuid(cnx, sid)
            if session is None:
                raise RuntimeError("failed to create chat session")
            return session
        finally:
            cnx.close()

    def ensure_session(
        self,
        session_id: str | None,
        *,
        title: str = "New chat",
        cwd: str = "",
        model: str = "",
        user_id: int | None = None,
    ) -> dict:
        if session_id:
            existing = self.get_session(session_id)
            if existing:
                return existing
        return self.create_session(
            session_id=session_id, title=title, cwd=cwd, model=model, user_id=user_id
        )

    def list_sessions(self, user_id: int | None = None) -> list[dict]:
        where = "WHERE c.user_id = %s" if user_id is not None else "WHERE c.user_id IS NULL"
        params: tuple = (user_id,) if user_id is not None else ()
        cnx = self._connect()
        try:
            cursor = cnx.cursor(dictionary=True)
            cursor.execute(f"{self._SESSION_SELECT} {where} ORDER BY c.updated_at DESC", params)
            rows = cursor.fetchall()
            cursor.close()
            return [self._session_from_row(row) for row in rows]
        finally:
            cnx.close()

    def get_session(self, session_id: str) -> dict | None:
        cnx = self._connect()
        try:
            return self._get_by_uuid(cnx, session_id)
        finally:
            cnx.close()

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

        cnx = self._connect()
        try:
            chat_id = self._chat_id(cnx, session_id)
            if chat_id is None:
                raise ValueError(f"unknown chat session: {session_id}")
            cursor = cnx.cursor()
            cursor.execute(
                "INSERT INTO messages (chat_id, role, content, model, created_at) "
                "VALUES (%s, %s, %s, %s, NOW())",
                (chat_id, role, content, model or None),
            )
            message_id = cursor.lastrowid
            if role == "user":
                cursor.execute(
                    "UPDATE chats SET name = CASE WHEN name IN (%s, %s) THEN %s ELSE name END, "
                    "model = CASE WHEN %s != '' THEN %s ELSE model END, updated_at = NOW() "
                    "WHERE id = %s",
                    (
                        *_DEFAULT_TITLES,
                        _title_from_message(content),
                        model or "",
                        model or "",
                        chat_id,
                    ),
                )
            else:
                cursor.execute(
                    "UPDATE chats SET model = CASE WHEN %s != '' THEN %s ELSE model END, "
                    "updated_at = NOW() WHERE id = %s",
                    (model or "", model or "", chat_id),
                )
            cursor.close()
        finally:
            cnx.close()
        now = _now()
        return {
            "id": str(message_id),
            "role": role,
            "content": content,
            "model": model,
            "createdAt": _iso(now),
            "ts": now,
        }

    def get_messages(self, session_id: str) -> list[dict]:
        cnx = self._connect()
        try:
            cursor = cnx.cursor(dictionary=True)
            cursor.execute(
                "SELECT m.id, m.role, m.content, m.model, m.created_at "
                "FROM messages m JOIN chats c ON c.id = m.chat_id "
                "WHERE c.session_uuid = %s ORDER BY m.id ASC",
                (session_id,),
            )
            rows = cursor.fetchall()
            cursor.close()
        finally:
            cnx.close()
        return [
            {
                "id": str(row["id"]),
                "role": row["role"],
                "content": row["content"],
                "model": row["model"] or "",
                "createdAt": _iso_dt(row["created_at"]),
                "ts": int(row["created_at"].timestamp()) if row["created_at"] else 0,
            }
            for row in rows
        ]

    def delete_session(self, session_id: str) -> bool:
        cnx = self._connect()
        try:
            cursor = cnx.cursor()
            cursor.execute("DELETE FROM chats WHERE session_uuid = %s", (session_id,))
            deleted = cursor.rowcount > 0
            cursor.close()
            return deleted
        finally:
            cnx.close()

    def _get_by_uuid(self, cnx: Any, session_id: str) -> dict | None:
        cursor = cnx.cursor(dictionary=True)
        cursor.execute(f"{self._SESSION_SELECT} WHERE c.session_uuid = %s", (session_id,))
        row = cursor.fetchone()
        cursor.close()
        return self._session_from_row(row) if row else None

    @staticmethod
    def _chat_id(cnx: Any, session_id: str) -> int | None:
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT id FROM chats WHERE session_uuid = %s", (session_id,))
        row = cursor.fetchone()
        cursor.close()
        return int(row["id"]) if row else None

    @staticmethod
    def _session_from_row(row: dict) -> dict:
        created = row["created_at"]
        updated = row["updated_at"]
        return {
            "id": row["session_uuid"],
            "sessionId": row["session_uuid"],
            "title": row["name"],
            "cwd": row["cwd"] or "",
            "model": row["model"] or "",
            "userId": row["user_id"],
            "messageCount": int(row["message_count"]),
            "createdAt": _iso_dt(created),
            "updatedAt": _iso_dt(updated),
            "created_at": int(created.timestamp()) if created else 0,
            "updated_at": int(updated.timestamp()) if updated else 0,
        }
