"""The marketplace: publish with consent, public profile, hire (unpaid locally, Stripe Connect when configured),
the hired pack in use, unpublish ends hires, ratings, reports, webhooks."""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from coworker import knowledge_pack, marketplace
from coworker.store import Store


@pytest.fixture(autouse=True)
def _env(monkeypatch):
    monkeypatch.setenv("COWORKER_OFFLINE", "1")
    monkeypatch.delenv("STRIPE_SECRET_KEY", raising=False)
    monkeypatch.delenv("MARKETPLACE_CREATOR_SHARE", raising=False)
    with patch("api_endpoints.coworker.common.owner_profile", return_value=("Natan Vidra", "natan@example.com")), \
         patch("api_endpoints.coworker.core.owner_profile", return_value=("Natan Vidra", "natan@example.com")):
        yield


@pytest.fixture
def s(tmp_path):
    store = Store(f"sqlite:///{tmp_path}/mk.db")
    store.create_coworker(1, "Natan Vidra", "natan@example.com", mode="demo")
    store.create_coworker(2, "Priya Shah", "priya@buyer.com", mode="demo")
    knowledge_pack.build(store, 1)
    knowledge_pack.freeze(store, 1)
    return store


def _publish(store: Store, **kw) -> dict:
    args = {"version": 1, "title": "AI Natan, billing engineer", "headline": "Ships billing code the careful way",
            "role": "engineering", "price_usd": 500, "consent": marketplace.consent_text(store, 1), **kw}
    return marketplace.publish(store, 1, **args)


def test_publish_requires_consent_a_frozen_version_and_sane_values(s):
    for bad, msg in [({"consent": "yes"}, "consent"), ({"version": 9}, "Save a knowledge pack version"),
                     ({"role": "pirate"}, "Pick a role"), ({"price_usd": 1}, "Price"), ({"title": " "}, "title")]:
        with pytest.raises(marketplace.MarketError, match=msg):
            _publish(s, **bad)
    listing = _publish(s)
    assert listing["slug"] == "ai-natan-vidra" and listing["status"] == "published"
    assert "evidence" not in str(listing["pack"]) and "quotes" not in str(listing["pack"])
    again = _publish(s, price_usd=600)  # republishing updates the same listing
    assert again["id"] == listing["id"] and again["price_usd"] == 600


def test_profile_and_directory(s):
    _publish(s)
    s.create_coworker(3, "Natan Vidra", "other@example.com", mode="demo")
    knowledge_pack.build(s, 3)
    knowledge_pack.freeze(s, 3)
    marketplace.publish(s, 3, version=1, title="Another", headline="", role="sales", price_usd=50,
                        consent=marketplace.consent_text(s, 3))
    assert s.one("SELECT slug FROM cw_listings WHERE user_id = 3")["slug"] == "ai-natan-vidra-2"
    p = marketplace.profile(s, marketplace.published(s, "ai-natan-vidra"))
    assert p["isAI"] and p["basedOn"] == "Natan Vidra" and p["styleRules"] and p["stats"]["activeHires"] == 0
    assert len(marketplace.directory(s)) == 2
    assert [x["slug"] for x in marketplace.directory(s, role="sales")] == ["ai-natan-vidra-2"]
    assert [x["slug"] for x in marketplace.directory(s, q="another")] == ["ai-natan-vidra-2"]
    with pytest.raises(marketplace.MarketError):
        marketplace.published(s, "nope")


def test_hire_without_stripe_activates_unpaid_and_uses_the_creators_pack(s):
    _publish(s)
    with pytest.raises(marketplace.MarketError):
        marketplace.hire(s, 1, "ai-natan-vidra")  # your own AI
    with pytest.raises(marketplace.MarketError):
        marketplace.hire(s, 99, "ai-natan-vidra")  # no coworker
    out = marketplace.hire(s, 2, "ai-natan-vidra")
    assert out["status"] == "active" and out["paid"] is False
    with pytest.raises(marketplace.MarketError):
        marketplace.hire(s, 2, "ai-natan-vidra")  # already hired
    pack = knowledge_pack.current(s, 2)
    assert any(r["id"] == "rule-money_decimal" for r in pack["style_rules"]) and "stats" not in pack
    earn = marketplace.earnings(s, 1)
    assert earn["activeHires"] == 1 and earn["monthlyEarningsUsd"] == 0  # unpaid hires earn nothing
    assert marketplace.my_hires(s, 2)[0]["title"] == "AI Natan, billing engineer"
    marketplace.end(s, 2, out["hireId"])
    assert marketplace.hired_pack(s, 2) is None
    with pytest.raises(marketplace.MarketError):
        marketplace.end(s, 2, out["hireId"])


def test_unpublish_ends_hires_and_hides_the_listing(s):
    _publish(s)
    marketplace.hire(s, 2, "ai-natan-vidra")
    marketplace.unpublish(s, 1)
    assert marketplace.hired_pack(s, 2) is None and marketplace.directory(s) == []
    assert s.one("SELECT status FROM cw_hires WHERE buyer_id = 2")["status"] == "ended"
    with pytest.raises(marketplace.MarketError):
        marketplace.unpublish(s, 2)


def test_hire_with_stripe_connect(s, monkeypatch):
    _publish(s)
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_x")
    fake = MagicMock()
    fake.checkout.Session.create.return_value = {"url": "https://checkout.stripe.com/x"}
    fake.Account.create.return_value = {"id": "acct_1"}
    fake.AccountLink.create.return_value = SimpleNamespace(url="https://connect.stripe.com/x")
    with patch("coworker.marketplace._stripe", return_value=fake):
        with pytest.raises(marketplace.MarketError, match="payouts"):
            marketplace.hire(s, 2, "ai-natan-vidra")  # creator hasn't connected payouts
        assert marketplace.connect_payouts(s, 1)["url"].startswith("https://connect")
        assert marketplace.connect_payouts(s, 1)["url"]  # resumes with the same account
        assert fake.Account.create.call_count == 1
        out = marketplace.hire(s, 2, "ai-natan-vidra")
    assert out["status"] == "checkout" and out["url"].startswith("https://checkout")
    kwargs = fake.checkout.Session.create.call_args.kwargs
    assert kwargs["subscription_data"]["transfer_data"] == {"destination": "acct_1"}
    assert kwargs["subscription_data"]["application_fee_percent"] == 30.0
    assert kwargs["line_items"][0]["price_data"]["unit_amount"] == 50000
    marketplace.apply_checkout(s, {"hire_id": str(out["hireId"])}, {"subscription": "sub_1"})
    assert marketplace.earnings(s, 1)["monthlyEarningsUsd"] == 350.0
    with patch("coworker.marketplace._stripe", return_value=fake):
        marketplace.apply_subscription_ended(s, {"metadata": {"hire_id": str(out["hireId"])}})
    assert s.get("cw_hires", out["hireId"])["status"] == "ended"
    marketplace.apply_subscription_ended(s, {"metadata": {}})  # unknown: ignored


def test_creator_share_bounds(monkeypatch):
    monkeypatch.setenv("MARKETPLACE_CREATOR_SHARE", "2")
    assert marketplace.creator_share() == 1.0
    monkeypatch.setenv("MARKETPLACE_CREATOR_SHARE", "x")
    assert marketplace.creator_share() == 0.7


def test_ratings_and_reports(s):
    _publish(s)
    with pytest.raises(marketplace.MarketError, match="Only people"):
        marketplace.rate(s, 2, "ai-natan-vidra", 5)
    marketplace.hire(s, 2, "ai-natan-vidra")
    with pytest.raises(marketplace.MarketError):
        marketplace.rate(s, 2, "ai-natan-vidra", 9)
    marketplace.rate(s, 2, "ai-natan-vidra", 4, "Solid PRs")
    with pytest.raises(marketplace.MarketError):
        marketplace.rate(s, 2, "ai-natan-vidra", 5)
    p = marketplace.profile(s, marketplace.published(s, "ai-natan-vidra"))
    assert p["stats"]["rating"] == 4.0 and p["reviews"][0]["text"] == "Solid PRs"
    with patch("observability.alert") as alert:
        marketplace.report(s, 2, "ai-natan-vidra", "Claims to be human")
    assert alert.called and marketplace.reports(s)[0]["reason"] == "Claims to be human"
    with pytest.raises(marketplace.MarketError):
        marketplace.report(s, 2, "ai-natan-vidra", " ")
    with pytest.raises(marketplace.MarketError):
        marketplace.report(s, 2, "nope", "x")


def test_routes(client, auth_headers, monkeypatch):
    h = auth_headers
    client.post("/api/coworker", json={"mode": "demo"}, headers=h)
    me = client.get("/api/coworker/marketplace/me", headers=h).get_json()
    assert me["listing"] is None and me["consent"].startswith("I, Natan Vidra") and me["versions"] == []
    client.post("/api/coworker/knowledge-pack/versions", headers=h)
    assert client.post("/api/coworker/marketplace/publish", json={"version": "x"}, headers=h).status_code == 400
    assert client.post("/api/coworker/marketplace/publish", json={"version": 1, "title": "t", "role": "sales",
                                                                    "priceUsd": 100, "consent": "no"}, headers=h).status_code == 400
    pub = client.post("/api/coworker/marketplace/publish", json={
        "version": 1, "title": "AI Natan", "role": "engineering", "priceUsd": 100, "consent": me["consent"]}, headers=h)
    assert pub.status_code == 201
    slug = pub.get_json()["slug"]
    assert client.get("/api/coworker/marketplace").get_json()["listings"][0]["slug"] == slug  # public
    assert client.get(f"/api/coworker/marketplace/ai/{slug}").get_json()["isAI"] is True
    assert client.get("/api/coworker/marketplace/ai/nope").status_code == 404
    assert client.post(f"/api/coworker/marketplace/ai/{slug}/hire", headers=h).status_code == 409  # own AI
    assert client.post(f"/api/coworker/marketplace/ai/{slug}/rate", json={"rating": "x"}, headers=h).status_code == 400
    assert client.post(f"/api/coworker/marketplace/ai/{slug}/rate", json={"rating": 5}, headers=h).status_code == 403
    with patch("observability.alert"):
        assert client.post(f"/api/coworker/marketplace/ai/{slug}/report", json={"reason": "spam"}, headers=h).status_code == 201
    assert client.post(f"/api/coworker/marketplace/ai/{slug}/report", json={}, headers=h).status_code == 400
    assert client.post("/api/coworker/marketplace/hires/99/end", headers=h).status_code == 404
    assert client.post("/api/coworker/marketplace/payouts", headers=h).status_code == 501
    assert client.get("/api/coworker/operator/marketplace/reports", headers=h).status_code == 403
    monkeypatch.setenv("COWORKER_OPERATOR_EMAILS", "ops@ourogen.ai")
    with patch("coworker.identity.verified_emails", return_value={"ops@ourogen.ai"}):
        assert len(client.get("/api/coworker/operator/marketplace/reports", headers=h).get_json()["reports"]) == 1
    assert client.post("/api/coworker/marketplace/unpublish", headers=h).status_code == 200


def test_webhook_routes_marketplace_events(s):
    from api_endpoints.payments import handler

    _publish(s)
    hire = marketplace.hire(s, 2, "ai-natan-vidra")
    with patch("coworker.store.get_store", return_value=s), \
         patch("coworker.marketplace.apply_checkout") as checkout, \
         patch("api_endpoints.payments.handler.get_connection", return_value=MagicMock()), \
         patch("api_endpoints.payments.handler.claim_stripe_event", return_value=True):
        handler._handle_webhook_event({"type": "checkout.session.completed", "data": {"object": {
            "id": "cs_1", "metadata": {"kind": "marketplace_hire", "hire_id": str(hire["hireId"])}}}})
        handler._handle_webhook_event({"type": "customer.subscription.updated", "data": {"object": {
            "metadata": {"kind": "marketplace_hire", "hire_id": str(hire["hireId"])}}}})
        handler._handle_webhook_event({"type": "customer.subscription.deleted", "data": {"object": {
            "metadata": {"kind": "marketplace_hire", "hire_id": str(hire["hireId"])}}}})
    assert checkout.called
    assert s.get("cw_hires", hire["hireId"])["status"] == "ended"
