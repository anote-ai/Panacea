"""Applies pending SQL files in database/migrations/ to the configured DB.

Tracks applied migrations in a schema_migrations table so each file runs
at most once. schema.sql seeds that table for migrations whose changes
are already part of the fresh-install schema, so this only does real work
against databases created before those changes landed (e.g. prod).

Run manually with `python -m database.migrate`, or automatically on
container start (see entrypoint.sh) — a MySQL named lock keeps concurrent
callers (e.g. multiple ECS tasks starting during a rolling deploy) from
applying the same migration twice at once.
"""
from __future__ import annotations

import os
from glob import glob

from database.db import get_connection

MIGRATIONS_DIR = os.path.join(os.path.dirname(__file__), "migrations")
LOCK_NAME = "anote_schema_migrations"
LOCK_TIMEOUT_SECONDS = 60


def _ensure_migrations_table(cnx) -> None:
    cursor = cnx.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version     VARCHAR(255) PRIMARY KEY,
            applied_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cursor.close()


def _applied_versions(cnx) -> set[str]:
    cursor = cnx.cursor()
    cursor.execute("SELECT version FROM schema_migrations")
    versions = {row[0] for row in cursor.fetchall()}
    cursor.close()
    return versions


def _pending_migrations(applied: set[str]) -> list[str]:
    paths = sorted(glob(os.path.join(MIGRATIONS_DIR, "*.sql")))
    return [p for p in paths if os.path.basename(p) not in applied]


def _apply_migration(cnx, path: str) -> None:
    version = os.path.basename(path)
    with open(path, encoding="utf-8") as f:
        sql = f.read()
    cursor = cnx.cursor()
    for statement in filter(None, (s.strip() for s in sql.split(";"))):
        cursor.execute(statement)
    cursor.execute("INSERT INTO schema_migrations (version) VALUES (%s)", (version,))
    cursor.close()
    print(f"[migrate] applied {version}")


def run_migrations() -> None:
    cnx = get_connection()
    try:
        lock_cursor = cnx.cursor()
        lock_cursor.execute("SELECT GET_LOCK(%s, %s)", (LOCK_NAME, LOCK_TIMEOUT_SECONDS))
        got_lock = lock_cursor.fetchone()[0] == 1
        lock_cursor.close()
        if not got_lock:
            raise RuntimeError(
                f"Could not acquire migration lock '{LOCK_NAME}' within "
                f"{LOCK_TIMEOUT_SECONDS}s; another migration may be stuck."
            )
        try:
            _ensure_migrations_table(cnx)
            applied = _applied_versions(cnx)
            pending = _pending_migrations(applied)
            if not pending:
                print("[migrate] no pending migrations")
            for path in pending:
                _apply_migration(cnx, path)
        finally:
            release_cursor = cnx.cursor()
            release_cursor.execute("SELECT RELEASE_LOCK(%s)", (LOCK_NAME,))
            release_cursor.close()
    finally:
        cnx.close()


if __name__ == "__main__":
    run_migrations()
