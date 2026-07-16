"""MySQL database connection and query helpers."""
from __future__ import annotations

import os
from typing import Any

try:
    import mysql.connector
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False


def get_connection() -> Any:
    if not MYSQL_AVAILABLE:
        raise RuntimeError("mysql-connector-python not installed")
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        database=os.environ.get("DB_NAME", "anote"),
        user=os.environ.get("DB_USER", "root"),
        password=os.environ.get("DB_PASSWORD", ""),
        autocommit=True,
    )


def get_user_by_email(cnx: Any, email: str) -> dict | None:
    cursor = cnx.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email = %s LIMIT 1", (email,))
    row = cursor.fetchone()
    cursor.close()
    return row


def create_user(cnx: Any, email: str, password_hash: str, name: str = "") -> int:
    cursor = cnx.cursor()
    cursor.execute(
        "INSERT INTO users (email, password_hash, name, created_at) VALUES (%s, %s, %s, NOW())",
        (email, password_hash, name),
    )
    user_id: int = cursor.lastrowid
    cursor.close()
    return user_id


# ---------------------------------------------------------------------------
# Folders
# ---------------------------------------------------------------------------

def create_folder(cnx: Any, user_id: int, name: str) -> int:
    cursor = cnx.cursor()
    cursor.execute(
        "INSERT INTO folders (user_id, name) VALUES (%s, %s)",
        (user_id, name),
    )
    folder_id: int = cursor.lastrowid
    cursor.close()
    return folder_id


def get_folders(cnx: Any, user_id: int) -> list[dict]:
    cursor = cnx.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, name, created_at FROM folders WHERE user_id = %s ORDER BY name",
        (user_id,),
    )
    rows = cursor.fetchall()
    cursor.close()
    return rows  # type: ignore[return-value]


def rename_folder(cnx: Any, folder_id: int, user_id: int, name: str) -> bool:
    cursor = cnx.cursor()
    cursor.execute(
        "UPDATE folders SET name = %s WHERE id = %s AND user_id = %s",
        (name, folder_id, user_id),
    )
    updated = cursor.rowcount > 0
    cursor.close()
    return updated


def delete_folder(cnx: Any, folder_id: int, user_id: int) -> bool:
    cursor = cnx.cursor()
    cursor.execute(
        "DELETE FROM folders WHERE id = %s AND user_id = %s",
        (folder_id, user_id),
    )
    deleted = cursor.rowcount > 0
    cursor.close()
    return deleted


# ---------------------------------------------------------------------------
# Documents
# ---------------------------------------------------------------------------

def create_document(cnx: Any, user_id: int, doc_uuid: str, filename: str,
                    chunk_count: int, folder_id: int | None = None,
                    chat_id: int | None = None) -> int:
    cursor = cnx.cursor()
    cursor.execute(
        "INSERT INTO documents (user_id, folder_id, chat_id, doc_uuid, filename, chunk_count) "
        "VALUES (%s, %s, %s, %s, %s, %s)",
        (user_id, folder_id, chat_id, doc_uuid, filename, chunk_count),
    )
    doc_id: int = cursor.lastrowid
    cursor.close()
    return doc_id


_DOCUMENT_SELECT = (
    "SELECT d.doc_uuid as id, d.filename, d.chunk_count, d.folder_id, d.chat_id, "
    "c.name as chat_name, d.created_at "
    "FROM documents d LEFT JOIN chats c ON d.chat_id = c.id"
)


def get_documents(cnx: Any, user_id: int, folder_id: int | None = None,
                  chat_id: int | None = None) -> list[dict]:
    cursor = cnx.cursor(dictionary=True)
    query = f"{_DOCUMENT_SELECT} WHERE d.user_id = %s"
    params: list[Any] = [user_id]
    if folder_id is not None:
        query += " AND d.folder_id = %s"
        params.append(folder_id)
    if chat_id is not None:
        query += " AND d.chat_id = %s"
        params.append(chat_id)
    query += " ORDER BY d.created_at DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    cursor.close()
    return rows  # type: ignore[return-value]


def get_document_by_uuid(cnx: Any, user_id: int, doc_uuid: str) -> dict | None:
    cursor = cnx.cursor(dictionary=True)
    cursor.execute(
        f"{_DOCUMENT_SELECT} WHERE d.user_id = %s AND d.doc_uuid = %s",
        (user_id, doc_uuid),
    )
    row = cursor.fetchone()
    cursor.close()
    return row  # type: ignore[return-value]


def delete_document(cnx: Any, user_id: int, doc_uuid: str) -> bool:
    cursor = cnx.cursor()
    cursor.execute(
        "DELETE FROM documents WHERE user_id = %s AND doc_uuid = %s",
        (user_id, doc_uuid),
    )
    deleted = cursor.rowcount > 0
    cursor.close()
    return deleted


def move_document(cnx: Any, user_id: int, doc_uuid: str, folder_id: int | None) -> bool:
    cursor = cnx.cursor()
    cursor.execute(
        "UPDATE documents SET folder_id = %s WHERE user_id = %s AND doc_uuid = %s",
        (folder_id, user_id, doc_uuid),
    )
    updated = cursor.rowcount > 0
    cursor.close()
    return updated


# ---------------------------------------------------------------------------
# Chats
# ---------------------------------------------------------------------------

def create_chat(cnx: Any, user_id: int, name: str = "New Chat") -> int:
    cursor = cnx.cursor()
    cursor.execute(
        "INSERT INTO chats (user_id, name) VALUES (%s, %s)",
        (user_id, name),
    )
    chat_id: int = cursor.lastrowid
    cursor.close()
    return chat_id


def get_chats(cnx: Any, user_id: int) -> list[dict]:
    cursor = cnx.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, name, created_at FROM chats WHERE user_id = %s ORDER BY created_at DESC",
        (user_id,),
    )
    rows = cursor.fetchall()
    cursor.close()
    return rows  # type: ignore[return-value]


def get_chat(cnx: Any, user_id: int, chat_id: int) -> dict | None:
    cursor = cnx.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, name, created_at FROM chats WHERE id = %s AND user_id = %s",
        (chat_id, user_id),
    )
    row = cursor.fetchone()
    cursor.close()
    return row  # type: ignore[return-value]


def rename_chat(cnx: Any, user_id: int, chat_id: int, name: str) -> bool:
    cursor = cnx.cursor()
    cursor.execute(
        "UPDATE chats SET name = %s WHERE id = %s AND user_id = %s",
        (name, chat_id, user_id),
    )
    updated = cursor.rowcount > 0
    cursor.close()
    return updated


def delete_chat(cnx: Any, user_id: int, chat_id: int) -> bool:
    cursor = cnx.cursor()
    cursor.execute(
        "DELETE FROM chats WHERE id = %s AND user_id = %s",
        (chat_id, user_id),
    )
    deleted = cursor.rowcount > 0
    cursor.close()
    return deleted


# ---------------------------------------------------------------------------
# Messages
# ---------------------------------------------------------------------------

def create_message(cnx: Any, chat_id: int, role: str, content: str, model: str | None = None) -> int:
    cursor = cnx.cursor()
    cursor.execute(
        "INSERT INTO messages (chat_id, role, content, model) VALUES (%s, %s, %s, %s)",
        (chat_id, role, content, model),
    )
    message_id: int = cursor.lastrowid
    cursor.close()
    return message_id


def get_messages(cnx: Any, chat_id: int) -> list[dict]:
    cursor = cnx.cursor(dictionary=True)
    cursor.execute(
        "SELECT role, content, created_at FROM messages WHERE chat_id = %s ORDER BY id",
        (chat_id,),
    )
    rows = cursor.fetchall()
    cursor.close()
    return rows  # type: ignore[return-value]
