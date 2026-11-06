"""The output scorecard: output, rates, quality, cost vs a hire, team view, CSV, weekly lines."""
from __future__ import annotations

from unittest.mock import patch

import pytest

from coworker import executor, orgs, scorecard, weekly
from coworker.connectors.base import encrypt_token
from coworker.connectors.devtools_demo import REPO
from coworker.engineering import review, runs
from coworker.store import Store


@pytest.fixture(autouse=True)
def _env(monkeypatch):
    monkeypatch.setenv("COWORKER_OFFLINE", "1")
    monkeypatch.delenv("COWORKER_ROLE_SALARIES", raising=False)
    with patch("api_endpoints.coworker.common.owner_profile", return_value=("Natan Vidra", "natan@example.com")), \
         patch("api_endpoints.coworker.core.owner_profile", return_value=("Natan Vidra", "natan@example.com")):
        yield


@pytest.fixture
def s(tmp_path):
    store = Store(f"sqlite:///{tmp_path}/sc.db")
    store.create_coworker(1, "Natan Vidra", "natan@example.com", mode="demo")
    return store


def _work(store: Store, user_id: int = 1) -> None:
    """A PR from the engineer (approved), a code review, and an edited + a rejected comment."""
    run = runs.create(store, user_id, source="jira:ACME-142")
    runs.plan(store, user_id, run["id"])
    done = runs.start(store, user_id, run["id"])
    executor.approve(store, user_id, done["action_id"])
    review.review_pull_request(store, user_id, REPO, 37)
    a = executor.propose(store, user_id, "github.comment", {"repo": REPO, "number": 37, "body": "hi"}, title="c1")
    executor.approve(store, user_id, a["id"], {"body": "hello"})
    b = executor.propose(store, user_id, "github.comment", {"repo": REPO, "number": 37, "body": "x"}, title="c2")
    executor.reject(store, user_id, b["id"], "no")


def test_empty_card(s):
    c = scorecard.card(s, 1, 7)
    assert c["totalOutput"] == 0 and c["rates"]["perHumanHour"] is None and c["quality"]["engineerPassRate"] is None
    assert c["vsHire"]["role"] == "sales" and c["cost"]["planUsd"] == 0  # pilot plan is free


def test_card_counts_output_quality_and_cost(s):
    _work(s)
    c = scorecard.card(s, 1, 7)
    o = c["output"]
    assert o["prsOpened"] == 1 and o["engineerRuns"] == 1 and o["ticketsShipped"] == 1 and o["prsReviewed"] == 1
    assert o["comments"] == 1 and c["totalOutput"] >= 4
    assert c["quality"]["engineerPassRate"] == 1.0 and c["quality"]["avgSlopScore"] >= 90
    assert c["quality"]["editsPerApproval"] > 0 and c["humanAttentionHours"] > 0
    assert c["rates"]["perHumanHour"] and c["rates"]["perDay"] > 0
    assert c["vsHire"]["role"] == "engineering" and c["vsHire"]["hireCostUsd"] == pytest.approx(200_000 / 365 * 7, rel=1e-3)
    assert c["activeHours"] >= 1
    s.update_coworker(1, plan="coworker", settings={"role": "marketing"})
    paid = scorecard.card(s, 1, 30)
    assert paid["cost"]["planUsd"] == 199 and paid["rates"]["perDollar"] and paid["vsHire"]["roleLabel"] == "Marketer"


def test_salary_override_and_bad_json(monkeypatch):
    monkeypatch.setenv("COWORKER_ROLE_SALARIES", '{"engineering": 150000, "custom": "x"}')
    assert scorecard.salaries()["engineering"] == 150000 and "custom" not in scorecard.salaries()
    monkeypatch.setenv("COWORKER_ROLE_SALARIES", "nope")
    assert scorecard.salaries()["engineering"] == 200_000


def test_csv_and_weekly_lines(s):
    _work(s)
    text = scorecard.to_csv(scorecard.card(s, 1, 7))
    assert text.startswith("metric,value") and "output.prsOpened,1" in text and "vs_hire.role,engineering" in text
    lines = scorecard.weekly_lines(s, 1)
    assert "1 PRs opened" in lines[1] and "benchmark" in lines[-1]
    headline, body = weekly.render(s, 1, weekly.report(s, 1))
    assert "Your scorecard:" in body and "Output this week" in body


def test_refresh_merged_marks_prs_from_github(s):
    s.insert("cw_eng_runs", {"user_id": 1, "title": "t", "status": "pr_opened", "repo": "a/b", "pr": {"number": "12"},
                             "created_at": "2026-01-01T00:00:00+00:00", "updated_at": "2026-01-01T00:00:00+00:00"})
    s.insert("cw_eng_runs", {"user_id": 1, "title": "t", "status": "pr_opened", "repo": "a/b", "pr": {"number": "13"},
                             "created_at": "2026-01-01T00:00:00+00:00", "updated_at": "2026-01-01T00:00:00+00:00"})
    assert scorecard.refresh_merged(s, 1) == 0  # no live GitHub
    s.upsert_connection(1, "github", token_enc=encrypt_token({"access_token": "t"}), status="connected")

    def fake(method, path, **kw):
        if path.endswith("/13"):
            raise RuntimeError("gone")
        return {"merged_at": "2026-01-02T00:00:00Z"}

    with patch("coworker.connectors.github.GitHubClient.request", side_effect=fake):
        assert scorecard.refresh_merged(s, 1) == 1
        assert scorecard.refresh_merged(s, 1) == 0  # already merged
    merged = [r for r in s.query("SELECT pr FROM cw_eng_runs WHERE user_id = 1") if (r["pr"] or {}).get("merged")]
    assert len(merged) == 1


def test_latest_evals_reads_history(tmp_path, monkeypatch):
    assert isinstance(scorecard.latest_evals(), dict)
    monkeypatch.setattr(scorecard.os.path, "join", lambda *a: str(tmp_path / "missing.jsonl"))
    assert scorecard.latest_evals() == {}


def test_team_scorecard(s):
    s.create_coworker(2, "Priya Shah", "priya@example.com", mode="demo")
    org = orgs.create(s, 1, "Anote", domain="example.com", email="natan@example.com")
    s.insert("cw_org_members", {"org_id": org["id"], "user_id": 2, "email": "priya@example.com", "role": "member",
                                "status": "active", "joined_at": "2026-01-01"})
    _work(s, 1)
    team = scorecard.team(s, 1, 7)
    assert len(team["members"]) == 2 and team["totals"]["totalOutput"] >= 4
    assert scorecard.team(s, 2, 7) is None  # not an admin
    assert scorecard.team(s, 99, 7) is None


def test_routes(client, auth_headers):
    h = auth_headers
    assert client.get("/api/coworker/scorecard", headers=h).status_code == 404
    client.post("/api/coworker", json={"mode": "demo"}, headers=h)
    body = client.get("/api/coworker/scorecard?days=30", headers=h).get_json()
    assert body["days"] == 30 and "output" in body
    assert client.get("/api/coworker/scorecard?days=abc", headers=h).get_json()["days"] == 7
    csv_resp = client.get("/api/coworker/scorecard?format=csv", headers=h)
    assert csv_resp.mimetype == "text/csv" and b"metric,value" in csv_resp.data
    assert client.get("/api/coworker/team/scorecard", headers=h).status_code == 403
    client.patch("/api/coworker", json={"settings": {"role": "engineering"}}, headers=h)
    assert client.get("/api/coworker/scorecard", headers=h).get_json()["vsHire"]["role"] == "engineering"
