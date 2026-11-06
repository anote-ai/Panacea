"""Pricing v3: the offered lineup, Pro and Enterprise, engineer-run caps, seat plans, and the margin analysis."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from coworker import billing, orgs, pricing
from coworker.engineering import runs
from coworker.store import Store, iso


@pytest.fixture(autouse=True)
def _env(monkeypatch):
    monkeypatch.setenv("COWORKER_OFFLINE", "1")
    for var in ("COWORKER_PRICING_V3", "COWORKER_ENFORCE_PLANS", "STRIPE_SECRET_KEY", "COWORKER_COST_PER_ENGINEER_RUN"):
        monkeypatch.delenv(var, raising=False)
    with patch("api_endpoints.coworker.common.owner_profile", return_value=("Natan Vidra", "natan@example.com")), \
         patch("api_endpoints.coworker.core.owner_profile", return_value=("Natan Vidra", "natan@example.com")):
        yield


@pytest.fixture
def s(tmp_path):
    store = Store(f"sqlite:///{tmp_path}/pr.db")
    store.create_coworker(1, "Natan Vidra", "natan@example.com", mode="demo")
    return store


def test_offered_lineup_switches_with_the_flag(s, monkeypatch):
    assert billing.offered() == billing.ORDER
    ids = [p["id"] for p in billing.summary(s, 1)["plans"]]
    assert "pro" not in ids and "pilot" in ids  # the current plan is always listed
    with pytest.raises(billing.PlanError, match="Coworker"):
        billing.change_plan(s, 1, "pro")
    monkeypatch.setenv("COWORKER_PRICING_V3", "1")
    assert billing.offered() == ["free", "pro", "enterprise"]
    plans = {p["id"]: p for p in billing.summary(s, 1)["plans"]}
    assert set(plans) == {"free", "pro", "enterprise", "pilot"}
    assert plans["pro"]["priceUsd"] == 50 and plans["pro"]["engineerRuns"] == 12 and plans["enterprise"]["perSeat"]
    with pytest.raises(billing.PlanError, match="Pro"):
        billing.change_plan(s, 1, "coworker")
    with pytest.raises(billing.PlanError, match="isn't configured"):
        billing.change_plan(s, 1, "pro")  # no Stripe on this server


def test_direction_by_price():
    assert billing.direction("free", "pro") == "upgrade"
    assert billing.direction("coworker", "pro") == "downgrade"
    assert billing.direction("pro", "pro") == "same"
    assert billing.direction("team", "enterprise") == "upgrade"


def test_engineer_runs_capped_when_plans_are_enforced(s, monkeypatch):
    monkeypatch.setenv("COWORKER_ENFORCE_PLANS", "1")
    s.update_coworker(1, plan="free")
    for _ in range(3):
        run = runs.create(s, 1, source="jira:ACME-142")
        runs.plan(s, 1, run["id"])
        assert runs.start(s, 1, run["id"])["status"] == "ready"
    run = runs.create(s, 1, source="jira:ACME-142")
    runs.plan(s, 1, run["id"])
    with pytest.raises(runs.RunError) as err:
        runs.start(s, 1, run["id"])
    assert err.value.code == "plan_limit" and "3 engineer runs" in str(err.value)
    s.update_coworker(1, plan="team")
    assert runs.start(s, 1, run["id"])["status"] == "ready"  # unlimited


def test_enterprise_is_a_seat_plan(s, monkeypatch):
    s.create_coworker(2, "Priya Shah", "priya@example.com", mode="demo")
    org = orgs.create(s, 1, "Anote", domain="example.com", email="natan@example.com")
    s.insert("cw_org_members", {"org_id": org["id"], "user_id": 2, "email": "priya@example.com", "role": "member",
                                "status": "active", "joined_at": iso()})
    s.update_coworker(1, plan="enterprise")
    assert billing.effective_plan(s, 2) == "enterprise" and billing.effective_plan(s, 1) == "enterprise"
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test")
    s.update_coworker(1, settings={"billing": {"subscription_id": "sub_1"}})
    fake = MagicMock()
    fake.Subscription.retrieve.return_value = {"items": {"data": [{"id": "si_1", "quantity": 1}]}}
    with patch("coworker.billing._stripe", return_value=fake):
        assert billing.sync_seats(s, s.get("cw_orgs", org["id"])) == 2
    fake.Subscription.modify.assert_called_once()


def test_margin_analysis_with_and_without_measured_runs(s, monkeypatch):
    report = pricing.analyze(s)
    assert report["runCostMeasured"] is False and report["engineerRunCostUsd"] == 1.5
    pro = next(p for p in report["plans"] if p["plan"] == "pro")
    assert pro["lineup"] == "v3" and pro["atCap"]["margin"] == pytest.approx((50 - 18) / 50, abs=1e-3)
    assert pro["suggestedRunCap"] == 13
    free = next(p for p in report["plans"] if p["plan"] == "free")
    assert free["p50"]["margin"] is None and free["suggestedRunCap"] is None
    s.insert("cw_eng_runs", {"user_id": 1, "title": "t", "status": "ready", "cost_micros": 3_000_000,
                             "created_at": iso(), "updated_at": iso()})
    s.insert("cw_runs", {"user_id": 1, "responsibility_id": 1, "trigger_key": "k", "status": "done", "created_at": iso(),
                         "cost_micros": 500_000})
    measured = pricing.analyze(s)
    assert measured["runCostMeasured"] and measured["engineerRunCostUsd"] == 3.0
    assert measured["profiles"]["p90"]["baseCostUsd"] == 0.5
    text = pricing.render(measured)
    assert "Pro" in text and "measured" in text
    monkeypatch.setenv("COWORKER_COST_PER_ENGINEER_RUN", "0.5")
    assert pricing.default_run_cost() == 0.5
    assert pricing._percentile([], 0.5) == 0.0


def test_operator_pricing_route(client, auth_headers, monkeypatch):
    h = auth_headers
    client.post("/api/coworker", json={"mode": "demo"}, headers=h)
    assert client.get("/api/coworker/operator/pricing", headers=h).status_code == 403
    monkeypatch.setenv("COWORKER_OPERATOR_EMAILS", "ops@ourogen.ai")
    with patch("coworker.identity.verified_emails", return_value={"ops@ourogen.ai"}):
        body = client.get("/api/coworker/operator/pricing", headers=h).get_json()
    assert body["users"] == 1 and any(p["plan"] == "enterprise" for p in body["plans"])


def test_plan_limit_route_status(client, auth_headers, monkeypatch):
    h = auth_headers
    client.post("/api/coworker", json={"mode": "demo"}, headers=h)
    monkeypatch.setenv("COWORKER_ENFORCE_PLANS", "1")
    with patch("coworker.billing.require", side_effect=billing.PlanError("You've used all 3 engineer runs")):
        rid = client.post("/api/coworker/engineer/runs", json={"source": "jira:ACME-142"}, headers=h).get_json()["id"]
        client.post(f"/api/coworker/engineer/runs/{rid}/plan", headers=h)
        resp = client.post(f"/api/coworker/engineer/runs/{rid}/start", headers=h)
    assert resp.status_code == 402 and resp.get_json()["code"] == "plan_limit"
