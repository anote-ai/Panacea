"""Tests for database/migrate.py — especially tolerance of statements whose
effect already exists in the DB (a long-lived dev DB whose schema_migrations
history doesn't match its actual schema)."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from mysql.connector.errors import Error as MySQLError

from database import migrate


def _mock_cnx_for_migration(execute_side_effect):
    cursor = MagicMock()
    cursor.execute.side_effect = execute_side_effect
    cnx = MagicMock()
    cnx.cursor.return_value = cursor
    return cnx, cursor


def test_apply_migration_skips_already_applied_statement(tmp_path):
    migration_file = tmp_path / "0099_test.sql"
    migration_file.write_text("ALTER TABLE documents ADD COLUMN folder_id INT;")

    already_exists = MySQLError(msg="Duplicate column name 'folder_id'", errno=1060)
    cnx, cursor = _mock_cnx_for_migration([already_exists, None])

    migrate._apply_migration(cnx, str(migration_file))

    # The ALTER raised (skipped), then the schema_migrations INSERT still ran.
    assert cursor.execute.call_count == 2
    insert_sql = cursor.execute.call_args_list[1].args[0]
    assert "INSERT INTO schema_migrations" in insert_sql
    cursor.close.assert_called_once()


def test_apply_migration_reraises_unrelated_error(tmp_path):
    migration_file = tmp_path / "0099_test.sql"
    migration_file.write_text("SELECT * FROM nonexistent_table;")

    real_error = MySQLError(msg="Table 'anote.nonexistent_table' doesn't exist", errno=1146)
    cnx, cursor = _mock_cnx_for_migration([real_error])

    with pytest.raises(MySQLError):
        migrate._apply_migration(cnx, str(migration_file))

    # Cursor is still closed even though the migration failed.
    cursor.close.assert_called_once()


def test_apply_migration_multiple_statements_all_applied(tmp_path):
    migration_file = tmp_path / "0099_test.sql"
    migration_file.write_text(
        "CREATE TABLE IF NOT EXISTS foo (id INT); ALTER TABLE foo ADD COLUMN bar INT;",
    )
    cnx, cursor = _mock_cnx_for_migration([None, None, None])

    migrate._apply_migration(cnx, str(migration_file))

    assert cursor.execute.call_count == 3


def test_apply_migration_semicolon_inside_comment_does_not_split_statement(tmp_path):
    """A `;` inside a `--` comment's prose must not be treated as a statement
    boundary — regression test for the real bug this session hit."""
    migration_file = tmp_path / "0099_test.sql"
    migration_file.write_text(
        "-- Safe to run against a database created before this feature existed;\n"
        "-- fresh installs already have this shape.\n"
        "\n"
        "CREATE TABLE IF NOT EXISTS foo (id INT);\n",
    )
    cnx, cursor = _mock_cnx_for_migration([None, None])

    migrate._apply_migration(cnx, str(migration_file))

    # Exactly one real statement (the CREATE TABLE) plus the tracking INSERT —
    # not split into a bogus fragment from the comment's semicolon.
    assert cursor.execute.call_count == 2
    first_statement = cursor.execute.call_args_list[0].args[0]
    assert "CREATE TABLE" in first_statement
    assert "fresh installs" not in first_statement


def test_strip_sql_comments_removes_full_line_comments_only():
    sql = "-- a comment; with a semicolon\nCREATE TABLE foo (id INT);"
    result = migrate._strip_sql_comments(sql)
    assert "-- a comment" not in result
    assert "CREATE TABLE foo (id INT);" in result


def test_pending_migrations_excludes_applied(tmp_path, monkeypatch):
    monkeypatch.setattr(migrate, "MIGRATIONS_DIR", str(tmp_path))
    (tmp_path / "0001_a.sql").write_text("SELECT 1;")
    (tmp_path / "0002_b.sql").write_text("SELECT 1;")

    pending = migrate._pending_migrations({"0001_a.sql"})
    assert [p.split("/")[-1].split("\\")[-1] for p in pending] == ["0002_b.sql"]


def test_run_migrations_acquires_and_releases_lock():
    cursor = MagicMock()
    cursor.fetchone.return_value = (1,)
    cnx = MagicMock()
    cnx.cursor.return_value = cursor

    with patch("database.migrate.get_connection", return_value=cnx), \
         patch("database.migrate._pending_migrations", return_value=[]):
        migrate.run_migrations()

    lock_calls = [c for c in cursor.execute.call_args_list if "GET_LOCK" in c.args[0]]
    release_calls = [c for c in cursor.execute.call_args_list if "RELEASE_LOCK" in c.args[0]]
    assert len(lock_calls) == 1
    assert len(release_calls) == 1
    cnx.close.assert_called_once()


def test_run_migrations_real_error_not_masked_by_lock_release_failure():
    """If a migration fails AND releasing the lock afterward also errors
    (e.g. the connection is left in a bad state), the original migration
    error must still be what propagates — not the lock-release failure."""
    cursor = MagicMock()
    cursor.fetchone.return_value = (1,)
    cursor.fetchall.return_value = []

    def _execute(sql, *args, **kwargs):
        if "RELEASE_LOCK" in sql:
            raise MySQLError(msg="Unread result found", errno=9999)
        return None

    cursor.execute.side_effect = _execute
    cnx = MagicMock()
    cnx.cursor.return_value = cursor

    def _boom(cnx, path):
        raise RuntimeError("boom from migration")

    with patch("database.migrate.get_connection", return_value=cnx), \
         patch("database.migrate._pending_migrations", return_value=["0099_test.sql"]), \
         patch("database.migrate._apply_migration", side_effect=_boom):
        with pytest.raises(RuntimeError, match="boom from migration"):
            migrate.run_migrations()


def test_run_migrations_raises_when_lock_not_acquired():
    cursor = MagicMock()
    cursor.fetchone.return_value = (0,)
    cnx = MagicMock()
    cnx.cursor.return_value = cursor

    with patch("database.migrate.get_connection", return_value=cnx):
        with pytest.raises(RuntimeError, match="Could not acquire migration lock"):
            migrate.run_migrations()
