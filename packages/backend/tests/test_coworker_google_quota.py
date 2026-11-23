"""Gmail quota-aware paging and recovery across independent sync workers."""
from __future__ import annotations

import json
import time
from unittest.mock import MagicMock, patch

import pytest

from coworker.connectors import google
from coworker.connectors.base import ConnectorError, Workspace, encrypt_token
from coworker.store import Store


@pytest.fixture
def store(tmp_path):
    db = Store(f"sqlite:///{tmp_path}/quota.db")
    db.create_coworker(1, "Owner", "owner@example.com", mode="live")
    db.upsert_connection(1, "google", status="connected", account_label="owner@example.com",
                         token_enc=encrypt_token({"access_token": "at", "expires_at": 9e9}))
    return db


def _cursor(store):
    return json.loads(store.get_connection_row(1, "google")["sync_cursor"] or "{}")


def _next_pass(store):
    cursor = _cursor(store)
    cursor["gmail_next_sync_at"] = 0
    store.upsert_connection(1, "google", sync_cursor=json.dumps(cursor))


def _message(mid):
    return {"id": mid, "threadId": mid, "internalDate": "1760000000000", "labelIds": ["INBOX"],
            "payload": {"headers": [{"name": "From", "value": "sender@example.com"}]}}


def test_backfill_resumes_at_next_page_and_replays_changes_since_start(store):
    listed = []

    def request(self, method, url, **kwargs):
        if url.endswith("/profile"):
            return {"emailAddress": "owner@example.com", "historyId": "120" if listed else "100"}
        if url.endswith("/messages"):
            params = kwargs["params"]
            listed.append(params)
            assert params["maxResults"] == 30
            if params.get("pageToken") == "page-2":
                return {"messages": [{"id": "m30"}, {"id": "m31"}]}
            return {"messages": [{"id": f"m{i}"} for i in range(30)], "nextPageToken": "page-2"}
        if url.endswith("/history"):
            assert kwargs["params"]["startHistoryId"] == "100"
            return {"historyId": "150", "history": [{"messagesAdded": [{"message": {"id": "m32"}}]}]}
        return _message(url.rsplit("/", 1)[-1])

    with patch.object(google.GoogleConnector, "_sync_calendar", return_value=0), \
            patch.object(google.GoogleConnector, "_sync_drive", return_value=0), \
            patch.object(google.GoogleConnector, "_request", request):
        assert Workspace(store, 1).sync() == {"google": 30}
        assert _cursor(store)["gmail_backfill_page_token"] == "page-2"
        assert _cursor(store)["gmail_backfill_history_id"] == "100"
        assert Workspace(store, 1).sync() == {"google": 0}  # another trigger in the same minute
        assert len(listed) == 1
        _next_pass(store)
        assert Workspace(store, 1).sync() == {"google": 2}
        assert _cursor(store)["gmail_history_id"] == "100"  # not the newer profile watermark
        assert listed[-1]["pageToken"] == "page-2"
        _next_pass(store)
        assert Workspace(store, 1).sync() == {"google": 1}
        assert _cursor(store)["gmail_history_id"] == "150"
    assert len(store.items(1, provider="gmail", limit=100)) == 33


def test_incremental_history_resumes_pending_ids_before_advancing_cursor(store):
    store.upsert_connection(1, "google", sync_cursor=json.dumps({"gmail_history_id": "100"}))
    history_calls = []

    def request(self, method, url, **kwargs):
        if url.endswith("/profile"):
            return {"emailAddress": "owner@example.com", "historyId": "150"}
        if url.endswith("/history"):
            history_calls.append(kwargs["params"])
            return {"historyId": "150", "history": [
                {"messagesAdded": [{"message": {"id": f"m{i}"}} for i in range(35)]}]}
        return _message(url.rsplit("/", 1)[-1])

    with patch.object(google.GoogleConnector, "_sync_calendar", return_value=0), \
            patch.object(google.GoogleConnector, "_sync_drive", return_value=0), \
            patch.object(google.GoogleConnector, "_request", request):
        assert Workspace(store, 1).sync() == {"google": 30}
        assert _cursor(store)["gmail_history_id"] == "100"
        assert len(_cursor(store)["gmail_pending_ids"]) == 5
        _next_pass(store)
        assert Workspace(store, 1).sync() == {"google": 5}
    assert len(history_calls) == 1
    assert _cursor(store)["gmail_history_id"] == "150"
    assert "gmail_pending_ids" not in _cursor(store)


def test_quota_403_cools_down_without_disconnect_or_repeat_requests(store):
    response = MagicMock(status_code=403)
    response.text = "Quota exceeded for quota metric 'Total Query Cost' and limit 'Units per minute per user'"
    response.json.return_value = {"error": {"code": 403, "message": response.text}}
    conn = google.GoogleConnector.from_row(store, store.get_connection_row(1, "google"))
    with patch("coworker.connectors.google.requests.request", return_value=response):
        with pytest.raises(ConnectorError) as exc:
            conn._request("GET", f"{google.GMAIL}/profile")
    assert exc.value.code == "rate_limited"

    store.upsert_connection(1, "google", status="error", error="Google API error 403")
    with patch.object(google.GoogleConnector, "_sync_calendar", return_value=0), \
            patch.object(google.GoogleConnector, "_sync_drive", return_value=0), \
            patch("coworker.connectors.google.requests.request", return_value=response) as request:
        assert Workspace(store, 1).sync() == {"google": 0}
        assert Workspace(store, 1).sync() == {"google": 0}
    assert request.call_count == 1
    assert store.get_connection_row(1, "google")["status"] == "connected"
    assert not store.get_connection_row(1, "google")["error"]
    assert _cursor(store)["gmail_next_sync_at"] > time.time() + 100


def test_gmail_slot_claim_is_atomic_across_connectors(store):
    row = store.get_connection_row(1, "google")
    one = google.GoogleConnector.from_row(store, row)
    two = google.GoogleConnector.from_row(store, row)
    assert one._claim_gmail_slot(store, 1)
    assert not two._claim_gmail_slot(store, 1)


def test_attachment_quota_replays_message_instead_of_skipping_it(store):
    attempts = []

    def request(self, method, url, **kwargs):
        if url.endswith("/profile"):
            return {"emailAddress": "owner@example.com", "historyId": "100"}
        if url.endswith("/messages"):
            return {"messages": [{"id": "m1"}]}
        return _message("m1")

    def attachments(self, db, user_id, item):
        attempts.append(item["external_id"])
        if len(attempts) == 1:
            raise ConnectorError("Gmail quota reached", "rate_limited")

    with patch.object(google.GoogleConnector, "_sync_calendar", return_value=0), \
            patch.object(google.GoogleConnector, "_sync_drive", return_value=0), \
            patch.object(google.GoogleConnector, "_request", request), \
            patch.object(google.GoogleConnector, "_ingest_attachments", attachments):
        assert Workspace(store, 1).sync() == {"google": 0}
        assert not store.items(1, provider="gmail")
        _next_pass(store)
        assert Workspace(store, 1).sync() == {"google": 1}
    assert attempts == ["m1", "m1"]


def test_mail_progress_survives_an_unrelated_drive_error(store):
    def request(self, method, url, **kwargs):
        if url.endswith("/profile"):
            return {"emailAddress": "owner@example.com", "historyId": "100"}
        if url.endswith("/messages"):
            return {"messages": [{"id": "m1"}]}
        return _message("m1")

    with patch.object(google.GoogleConnector, "_sync_calendar", return_value=0), \
            patch.object(google.GoogleConnector, "_sync_drive", side_effect=ConnectorError("Drive unavailable")), \
            patch.object(google.GoogleConnector, "_request", request):
        assert Workspace(store, 1).sync() == {}
    assert _cursor(store)["gmail_history_id"] == "100"
    assert len(store.items(1, provider="gmail")) == 1
