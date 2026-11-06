"""The one-month trial: goals, weekly and final reports, decisions, and the operator view."""
from __future__ import annotations

from datetime import timedelta
from unittest.mock import patch

import pytest

from coworker import executor, trial
from coworker.connectors.devtools_demo import REPO
from coworker.engineering import runs
from coworker.store import Store, iso, utcnow


@pytest.fixture(autouse=True)
def _env(monkeypatch):
    monkeypatch.setenv("COWORKER_OFFLINE", "1")
    with patch("api_endpoints.coworker.common.owner_profile", return_value=("Natan Vidra", "natan@example.com")), \
         patch("api_endpoints.coworker.core.owner_profile", return_value=("Natan Vidra", "natan@example.com")):
        yield


@pytest.fixture
def s(tmp_path):
    store = Store(f"sqlite:///{tmp_path}/trial.db")
    store.create_coworker(1, "Natan Vidra", "natan@example.com", mode="demo")
    return store


def _age(store: Store, days: int) -> dict:
    """Move the running trial's start back ``days`` days."""
    t = trial.current(store, 1)
    assert t is not None
    start = utcnow() - timedelta(days=days)
    store.update("cw_trials", t["id"], 1, {"started_at": iso(start), "ends_at": iso(start + timedelta(days=trial.TRIAL_DAYS))})
    fresh = trial.current(store, 1)
    assert fresh is not None
    return fresh


def _ship_a_pr(store: Store) -> None:
    run = runs.create(store, 1, source="jira:ACME-142")
    runs.plan(store, 1, run["id"])
    executor.approve(store, 1, runs.start(store, 1, run["id"])["action_id"])


def test_start_with_default_goals_and_validation(s):
    with pytest.raises(trial.TrialError):
        trial.start(s, 1, "astronaut")
    with pytest.raises(trial.TrialError):
        trial.start(s, 2, "sales")  # no coworker
    t = trial.start(s, 1, "engineering")
    assert t["status"] == "active" and [g["metric"] for g in t["goals"]][0] == "output.prsOpened"
    assert t["approver"] == "natan@example.com"
    assert (s.get_coworker(1)["settings"] or {})["role"] == "engineering"
    with pytest.raises(trial.TrialError) as err:
        trial.start(s, 1, "sales")
    assert err.value.code == "conflict"
    for bad in ([], [{"metric": "nope", "target": 1}], [{"metric": "totalOutput", "target": "x"}],
                [{"metric": "quality.acceptance", "target": 2}], [{"metric": "totalOutput", "target": 0}]):
        with pytest.raises(trial.TrialError):
            trial.update_goals(s, 1, bad)


def test_goals_lock_after_week_one(s):
    trial.start(s, 1, "sales")
    t = trial.update_goals(s, 1, [{"metric": "output.emails", "target": 50}])
    assert t["goals"] == [{"metric": "output.emails", "target": 50.0, "label": "Emails handled"}]
    _age(s, 8)
    with pytest.raises(trial.TrialError) as err:
        trial.update_goals(s, 1, [{"metric": "output.emails", "target": 5}])
    assert err.value.code == "conflict"
    assert trial.serialize(trial.current(s, 1))["goalsLocked"]


def test_progress_tracks_goals_against_the_scorecard(s):
    trial.start(s, 1, "engineering", goals=[{"metric": "output.prsOpened", "target": 1},
                                             {"metric": "quality.engineerPassRate", "target": 0.5},
                                             {"metric": "output.prsMerged", "target": 3}])
    _ship_a_pr(s)
    prog = trial.progress(s, 1, trial.current(s, 1))
    by = {g["metric"]: g for g in prog["goals"]}
    assert by["output.prsOpened"]["met"] and by["quality.engineerPassRate"]["met"]
    assert not by["output.prsMerged"]["met"] and prog["met"] == 2 and prog["of"] == 30


def test_weekly_then_final_report_then_decisions(s):
    trial.start(s, 1, "engineering", goals=[{"metric": "output.prsOpened", "target": 1}])
    assert trial.tick(s, 1) == ""  # week 0: nothing yet
    _age(s, 7)
    assert trial.tick(s, 1) == "week-1"
    assert trial.tick(s, 1) == ""  # once per week
    _ship_a_pr(s)
    _age(s, 31)
    assert trial.tick(s, 1) == "final"
    t = trial.current(s, 1)
    assert t["status"] == "ended" and t["outcome"] == {"met": 1, "of": 1}
    assert [r["final"] for r in t["reports"]] == [False, True]
    inbox = [i for i in s.items(1, kind="email") if "trial" in i["subject"].lower()]
    assert any("End-of-trial report" in i["body"] and "1 of 1 goals met" in i["body"] for i in inbox)
    assert trial.tick(s, 1) == ""  # ended: nothing more

    extended = trial.decide(s, 1, "extend")
    assert extended["status"] == "extended" and extended["outcome"]["extended"]
    with pytest.raises(trial.TrialError):
        trial.decide(s, 1, "extend")
    with pytest.raises(trial.TrialError):
        trial.decide(s, 1, "convert", plan="free")
    with pytest.raises(trial.TrialError):
        trial.decide(s, 1, "maybe")
    assert trial.decide(s, 1, "convert", plan="coworker")["outcome"]["plan"] == "coworker"


def test_cancel_and_missing_trial(s):
    with pytest.raises(trial.TrialError):
        trial.decide(s, 1, "cancel")
    with pytest.raises(trial.TrialError):
        trial.update_goals(s, 1, [{"metric": "totalOutput", "target": 1}])
    assert trial.tick(s, 1) == ""
    trial.start(s, 1, "marketing")
    assert trial.decide(s, 1, "cancel")["status"] == "cancelled"
    assert trial.start(s, 1, "marketing")["status"] == "active"  # a new trial after cancelling


def test_operator_view_flags_and_notes(s):
    trial.start(s, 1, "engineering")
    executor.propose(s, 1, "github.pr", {"repo": REPO, "branch": "b", "title": "t", "files": []}, title="Risky PR",
                     extra_risks=[{"code": "checks_failed", "message": "The tests failed."}])
    overview = trial.operator_overview(s)
    assert overview[0]["owner"] == "natan@example.com" and overview[0]["flags"]["waiting"] == 1
    assert trial.flagged(s, 1)["waiting"][0]["title"] == "Risky PR"
    trial.operator_note(s, 99, overview[0]["id"], "I looked at the failing PR; the fixture needs updating.")
    assert any(a["kind"] == "operator" for a in s.activity(1))
    with pytest.raises(trial.TrialError):
        trial.operator_note(s, 99, overview[0]["id"], "  ")
    with pytest.raises(trial.TrialError):
        trial.operator_note(s, 99, 999, "x")


def test_routes(client, auth_headers, monkeypatch):
    h = auth_headers
    client.post("/api/coworker", json={"mode": "demo"}, headers=h)
    empty = client.get("/api/coworker/trial", headers=h).get_json()
    assert empty["trial"] is None and "engineering" in empty["defaults"]
    assert client.post("/api/coworker/trial", json={"role": "x"}, headers=h).status_code == 400
    created = client.post("/api/coworker/trial", json={"role": "sales"}, headers=h)
    assert created.status_code == 201 and created.get_json()["trial"]["progress"]["day"] == 0
    assert client.post("/api/coworker/trial", json={"role": "sales"}, headers=h).status_code == 409
    assert client.put("/api/coworker/trial/goals", json={"goals": "x"}, headers=h).status_code == 400
    assert client.put("/api/coworker/trial/goals", json={"goals": [{"metric": "nope", "target": 1}]}, headers=h).status_code == 400
    ok = client.put("/api/coworker/trial/goals", json={"goals": [{"metric": "output.emails", "target": 10}]}, headers=h)
    assert ok.get_json()["trial"]["goals"][0]["target"] == 10
    assert client.post("/api/coworker/trial/decide", json={"choice": "nah"}, headers=h).status_code == 400
    with patch("coworker.billing.change_plan", return_value={"status": "checkout", "url": "https://stripe"}):
        conv = client.post("/api/coworker/trial/decide", json={"choice": "convert", "plan": "coworker"}, headers=h)
    assert conv.get_json()["billing"]["status"] == "checkout"
    from coworker import billing

    with patch("coworker.billing.change_plan", side_effect=billing.PlanError("not yet")):
        conv = client.post("/api/coworker/trial/decide", json={"choice": "convert", "plan": "coworker"}, headers=h)
    assert conv.get_json()["billing"]["status"] == "error"

    assert client.get("/api/coworker/operator/trials", headers=h).status_code == 403
    assert client.get("/api/coworker/operator/trials/1", headers=h).status_code == 403
    assert client.post("/api/coworker/operator/trials/1/notes", json={"text": "x"}, headers=h).status_code == 403
    monkeypatch.setenv("COWORKER_OPERATOR_EMAILS", "ops@ourogen.ai")
    with patch("coworker.identity.verified_emails", return_value={"ops@ourogen.ai"}):
        assert client.get("/api/coworker/operator/trials", headers=h).status_code == 200
        detail = client.get("/api/coworker/operator/trials/1", headers=h).get_json()
        assert "flags" in detail and "activity" in detail
        assert client.get("/api/coworker/operator/trials/99", headers=h).status_code == 404
        assert client.post("/api/coworker/operator/trials/1/notes", json={"text": "hi"}, headers=h).status_code == 201
        assert client.post("/api/coworker/operator/trials/1/notes", json={"text": ""}, headers=h).status_code == 400
