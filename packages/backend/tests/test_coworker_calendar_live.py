"""Calendar chat reads live events and never calls an unreadable calendar free."""
from __future__ import annotations

from datetime import timedelta
from unittest.mock import patch

import pytest

from coworker import brain, drafting, sync_jobs, tools
from coworker.connectors.base import ConnectorError
from coworker.connectors.google import GoogleConnector, _calendar_time
from coworker.store import Store, iso, utcnow


@pytest.fixture
def live_store(tmp_path):
    store = Store(f"sqlite:///{tmp_path}/calendar.db")
    store.create_coworker(1, "Natan Vidra", "vidranatan@gmail.com", mode="live")
    return store


def _event(store, event_id="meeting"):
    start = iso(utcnow() + timedelta(hours=4))
    store.add_item(1, {
        "provider": "gcal", "external_id": event_id, "thread_id": f"event-{event_id}", "kind": "event",
        "subject": "Monday meeting", "occurred_at": start,
        "meta": {"start": start, "end": iso(utcnow() + timedelta(hours=5))},
    })


def test_calendar_fetches_google_independent_of_mail_backfill(live_store):
    live_store.upsert_connection(1, "google", status="error", account_label="vidranatan@gmail.com",
                                 error="Gmail backfill failed", token_enc="mock-token")
    conn = GoogleConnector(live_store, 1, {}, {})

    def fetch_calendar(store, user_id, **kwargs):
        _event(store)
        return 1

    with patch.object(GoogleConnector, "from_row", return_value=conn), \
         patch.object(conn, "_sync_calendar", side_effect=fetch_calendar) as fetch, \
         patch.object(conn, "_sync_gmail") as gmail:
        events, summary = tools.run("calendar", {"days": 7}, tools.ToolContext(live_store, 1))
    assert len(events) == 1 and events[0]["title"] == "Monday meeting"
    assert "vidranatan@gmail.com" in summary
    assert fetch.call_count == 1
    gmail.assert_not_called()


def test_missing_or_failed_connection_does_not_claim_clear_calendar(live_store):
    ctx = tools.ToolContext(live_store, 1)
    events, summary = tools.run("calendar", {}, ctx)
    assert "connected calendar" in events["error"] and "Couldn't check" in summary
    slots, summary = tools.run("find_free_slots", {}, ctx)
    assert "connected calendar" in slots["error"] and "Couldn't check" in summary
    assert drafting.slot_lines(live_store, 1) == ("", [])
    with patch("coworker.brain.llm.available", return_value=False):
        reply = list(brain.run_turn(live_store, 1, None, "What's on my calendar this week?"))
    assert "connected calendar" in "".join(value for kind, value in reply if kind == "text")

    live_store.upsert_connection(1, "google", status="connected", account_label="vidranatan@gmail.com",
                                 token_enc="mock-token")
    _event(live_store, "stale")
    conn = GoogleConnector(live_store, 1, {}, {})
    with patch.object(GoogleConnector, "from_row", return_value=conn), \
         patch.object(conn, "_sync_calendar", side_effect=ConnectorError("Calendar API failed")):
        events, _ = tools.run("calendar", {}, ctx)
        slots, _ = tools.run("find_free_slots", {}, ctx)
    assert "Calendar API failed" in events["error"]
    assert "Calendar API failed" in slots["error"]


def test_google_calendar_paginates_and_removes_cancelled_cache_entries(live_store):
    _event(live_store, "cancelled")
    conn = GoogleConnector(live_store, 1, {}, {})
    now = utcnow()

    def event(event_id):
        return {"id": event_id, "summary": event_id, "start": {"dateTime": iso(now + timedelta(hours=4))},
                "end": {"dateTime": iso(now + timedelta(hours=5))}}

    pages = [
        {"items": [event("one")], "nextPageToken": "page-2"},
        {"items": [event("two"), {"id": "cancelled", "status": "cancelled"}]},
    ]
    with patch.object(conn, "_request", side_effect=pages) as request:
        assert conn._sync_calendar(live_store, 1, start=now - timedelta(days=1),
                                   end=now + timedelta(days=7)) == 2
    assert request.call_args_list[1].kwargs["params"]["pageToken"] == "page-2"
    ids = {row["external_id"] for row in live_store.items(1, provider="gcal")}
    assert ids == {"one", "two"}


def test_all_day_google_dates_use_calendar_timezone():
    assert _calendar_time("2026-11-23", "America/New_York").startswith("2026-11-23T05:00:00")


def test_failed_sync_is_reported_and_retried(live_store, app):
    live_store.upsert_connection(1, "google", status="connected", account_label="vidranatan@gmail.com",
                                 token_enc="mock-token")
    with app.app_context(), patch.object(GoogleConnector, "from_row", return_value=GoogleConnector(live_store, 1, {}, {})), \
         patch.object(GoogleConnector, "sync", side_effect=ConnectorError("Gmail timed out")):
        job = sync_jobs.request(live_store, 1)
        assert sync_jobs.run_job(live_store, job["id"])["status"] == "error"
    assert live_store.get_connection_row(1, "google")["status"] == "error"
    assert "Gmail timed out" in sync_jobs.status(live_store, 1)["job"]["error"]
    with app.app_context(), patch.object(GoogleConnector, "from_row", return_value=GoogleConnector(live_store, 1, {}, {})), \
         patch.object(GoogleConnector, "sync", return_value=1), \
         patch("api_endpoints.coworker.core.refresh_knowledge"):
        job = sync_jobs.request(live_store, 1)
        assert sync_jobs.run_job(live_store, job["id"])["status"] == "done"
    assert live_store.get_connection_row(1, "google")["status"] == "connected"
