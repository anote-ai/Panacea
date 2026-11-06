"""The marketplace: publish your AI, and hire other people's.

**Publish.** A creator picks a frozen knowledge-pack version, a title, a monthly
price, and records consent. The public profile shows who it's based on, that
it's an AI, its skills, style rules and playbooks (never evidence links or
titles, which can name private repos and people), its scorecard numbers, and
its price.

**Hire.** A buyer hires a published AI into their own workspace. Their engineer
and code reviewer then work from the creator's pack instead of their own, on
the buyer's own data and connections. The creator only ever sees how many
hires they have and what they earned; never the buyer's data.

**Payments.** Stripe Checkout (subscription) with Stripe Connect: the creator's
share (``MARKETPLACE_CREATOR_SHARE``, default 70%) is transferred to their
connected account, Ourogen keeps the rest as an application fee. Without
Stripe configured (local, demo), hires activate unpaid and say so.

**Controls.** Unpublishing removes the listing and ends every active hire.
Buyers who hired an AI can rate it once. Anyone signed in can report a listing;
operators see reports.
"""
from __future__ import annotations

import os
import re
from typing import Any

from coworker.store import Store, iso

CONSENT = "I, {name}, agree to publish an AI built from my work, labeled as an AI, for others to hire."
MIN_PRICE, MAX_PRICE = 10, 20_000
ROLES = ("engineering", "sales", "marketing", "healthcare", "operations", "assistant")


class MarketError(Exception):
    def __init__(self, message: str, code: str = "bad_request") -> None:
        super().__init__(message)
        self.code = code


def creator_share() -> float:
    try:
        share = float(os.environ.get("MARKETPLACE_CREATOR_SHARE", "0.7"))
    except ValueError:
        share = 0.7
    return min(max(share, 0.0), 1.0)


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60] or "ai"


def public_pack(pack: dict[str, Any]) -> dict[str, Any]:
    """What a buyer may see: no evidence titles or links, no quotes, no stats about private sources."""
    return {
        "skills": [{"id": s["id"], "name": s["name"], "weight": s.get("weight", 0)} for s in pack.get("skills") or []],
        "style_rules": [{"id": r["id"], "text": r["text"], "check": r.get("check", "")} for r in pack.get("style_rules") or []],
        "playbooks": [{"id": p["id"], "title": p["title"], "steps": list(p.get("steps") or [])}
                      for p in pack.get("playbooks") or []],
    }


def consent_text(store: Store, user_id: int) -> str:
    name = (store.get_coworker(user_id) or {}).get("owner_name") or "the creator"
    return CONSENT.format(name=name)


def publish(store: Store, user_id: int, *, version: int, title: str, headline: str, role: str, price_usd: int,
            consent: str) -> dict[str, Any]:
    if consent.strip() != consent_text(store, user_id):
        raise MarketError("Type the consent statement exactly as shown")
    row = store.one("SELECT * FROM cw_knowledge_packs WHERE user_id = %s AND version = %s AND status = 'frozen'",
                    (user_id, int(version)))
    if not row:
        raise MarketError("Save a knowledge pack version first, then publish that version", "not_found")
    if role not in ROLES:
        raise MarketError(f"Pick a role: {', '.join(ROLES)}")
    if not (MIN_PRICE <= int(price_usd) <= MAX_PRICE):
        raise MarketError(f"Price must be between ${MIN_PRICE} and ${MAX_PRICE:,} a month")
    title, headline = title.strip()[:120], headline.strip()[:300]
    if not title:
        raise MarketError("Give your AI a title")
    existing = store.one("SELECT * FROM cw_listings WHERE user_id = %s", (user_id,))
    values = {"title": title, "headline": headline, "role": role, "pack_version": int(version),
              "pack": public_pack(row.get("pack") or {}), "price_usd": int(price_usd), "status": "published",
              "consent": {"text": consent.strip(), "at": iso()}, "updated_at": iso()}
    if existing:
        store.update("cw_listings", existing["id"], user_id, values)
        listing_id = existing["id"]
    else:
        base = _slug(f"ai {(store.get_coworker(user_id) or {}).get('owner_name') or title}")
        slug, n = base, 1
        while store.one("SELECT id FROM cw_listings WHERE slug = %s", (slug,)):
            n += 1
            slug = f"{base}-{n}"
        listing_id = store.insert("cw_listings", {"user_id": user_id, "slug": slug, "created_at": iso(), **values})
    store.log(user_id, "marketplace", f"Published “{title}” (knowledge pack v{version}) at ${price_usd}/month")
    out = store.get("cw_listings", listing_id, user_id)
    assert out is not None
    return out


def unpublish(store: Store, user_id: int) -> dict[str, Any]:
    listing = store.one("SELECT * FROM cw_listings WHERE user_id = %s", (user_id,))
    if not listing:
        raise MarketError("Nothing published", "not_found")
    store.update("cw_listings", listing["id"], user_id, {"status": "unpublished", "updated_at": iso()})
    ended = 0
    for hire in store.query("SELECT * FROM cw_hires WHERE listing_id = %s AND status IN ('active', 'pending')", (listing["id"],)):
        _end_hire(store, hire, "The creator unpublished this AI.")
        ended += 1
    store.log(user_id, "marketplace", f"Unpublished “{listing['title']}” and ended {ended} hire(s)")
    out = store.get("cw_listings", listing["id"], user_id)
    assert out is not None
    return out


def _stats(store: Store, listing: dict[str, Any]) -> dict[str, Any]:
    from coworker import scorecard

    card = scorecard.card(store, int(listing["user_id"]), 30)
    ratings = store.query("SELECT rating FROM cw_listing_reviews WHERE listing_id = %s", (listing["id"],))
    hires = store.one("SELECT COUNT(*) AS n FROM cw_hires WHERE listing_id = %s AND status = 'active'", (listing["id"],))
    return {"workDone30d": card["totalOutput"], "acceptance": card["quality"]["acceptance"],
            "engineerPassRate": card["quality"]["engineerPassRate"], "avgSlopScore": card["quality"]["avgSlopScore"],
            "rating": round(sum(r["rating"] for r in ratings) / len(ratings), 1) if ratings else None,
            "ratings": len(ratings), "activeHires": int((hires or {}).get("n") or 0)}


def profile(store: Store, listing: dict[str, Any]) -> dict[str, Any]:
    coworker = store.get_coworker(int(listing["user_id"])) or {}
    reviews = store.query("SELECT rating, text, created_at FROM cw_listing_reviews WHERE listing_id = %s "
                          "ORDER BY id DESC LIMIT 20", (listing["id"],))
    pack = listing.get("pack") or {}
    return {"slug": listing["slug"], "title": listing["title"], "headline": listing.get("headline") or "",
            "basedOn": coworker.get("owner_name") or "", "isAI": True, "role": listing["role"],
            "priceUsd": listing["price_usd"], "packVersion": listing["pack_version"], "status": listing["status"],
            "skills": pack.get("skills") or [], "styleRules": pack.get("style_rules") or [],
            "playbooks": pack.get("playbooks") or [], "stats": _stats(store, listing),
            "reviews": [{"rating": r["rating"], "text": r["text"], "at": r["created_at"]} for r in reviews]}


def directory(store: Store, role: str = "", q: str = "") -> list[dict[str, Any]]:
    rows = store.query("SELECT * FROM cw_listings WHERE status = 'published' ORDER BY id DESC LIMIT 200")
    out = []
    for r in rows:
        if role and r["role"] != role:
            continue
        skills = [s["name"] for s in (r.get("pack") or {}).get("skills") or []]
        blob = f"{r['title']} {r.get('headline') or ''} {' '.join(skills)}".lower()
        if q and q.lower() not in blob:
            continue
        coworker = store.get_coworker(int(r["user_id"])) or {}
        out.append({"slug": r["slug"], "title": r["title"], "headline": r.get("headline") or "", "role": r["role"],
                    "basedOn": coworker.get("owner_name") or "", "priceUsd": r["price_usd"], "skills": skills[:6],
                    "stats": _stats(store, r)})
    return out


def published(store: Store, slug: str) -> dict[str, Any]:
    listing = store.one("SELECT * FROM cw_listings WHERE slug = %s AND status = 'published'", (slug,))
    if not listing:
        raise MarketError("No such AI", "not_found")
    return listing


# -- hiring -----------------------------------------------------------------------------

def _stripe() -> Any:
    import stripe

    stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "")
    return stripe


def hire(store: Store, buyer_id: int, slug: str) -> dict[str, Any]:
    listing = published(store, slug)
    if int(listing["user_id"]) == buyer_id:
        raise MarketError("That's your own AI", "conflict")
    if not store.get_coworker(buyer_id):
        raise MarketError("Set up your coworker first", "not_found")
    if store.one("SELECT id FROM cw_hires WHERE buyer_id = %s AND listing_id = %s AND status IN ('active', 'pending')",
                 (buyer_id, listing["id"])):
        raise MarketError("You've already hired this AI", "conflict")
    hire_id = store.insert("cw_hires", {
        "buyer_id": buyer_id, "listing_id": listing["id"], "creator_id": listing["user_id"], "status": "pending",
        "price_usd": listing["price_usd"], "creator_share": creator_share(), "pack_version": listing["pack_version"],
        "created_at": iso(), "updated_at": iso()})
    creator = store.get_coworker(int(listing["user_id"])) or {}
    account = ((creator.get("settings") or {}).get("connect") or {}).get("account_id")
    if not os.environ.get("STRIPE_SECRET_KEY"):
        activate(store, hire_id, paid=False)
        return {"status": "active", "hireId": hire_id, "paid": False,
                "note": "Payments aren't configured on this server, so this hire is active and unpaid."}
    if not account:
        store.update("cw_hires", hire_id, None, {"status": "cancelled", "updated_at": iso()})
        raise MarketError("This creator hasn't finished setting up payouts yet", "conflict")
    base = os.environ.get("FRONTEND_URL", "http://localhost:3000").rstrip("/")
    session = _stripe().checkout.Session.create(
        mode="subscription",
        line_items=[{"quantity": 1, "price_data": {"currency": "usd", "unit_amount": int(listing["price_usd"]) * 100,
                                                   "recurring": {"interval": "month"},
                                                   "product_data": {"name": f"{listing['title']} (AI) on Ourogen"}}}],
        success_url=f"{base}/app/coworker/marketplace?hired={listing['slug']}",
        cancel_url=f"{base}/app/coworker/marketplace?cancelled={listing['slug']}",
        metadata={"kind": "marketplace_hire", "hire_id": str(hire_id), "buyer_id": str(buyer_id)},
        subscription_data={"metadata": {"kind": "marketplace_hire", "hire_id": str(hire_id)},
                           "application_fee_percent": round((1 - creator_share()) * 100, 2),
                           "transfer_data": {"destination": account}},
    )
    return {"status": "checkout", "hireId": hire_id, "url": session["url"] if isinstance(session, dict) else session.url}


def activate(store: Store, hire_id: int, paid: bool = True, subscription_id: str = "") -> None:
    hire = store.get("cw_hires", hire_id)
    if not hire or hire["status"] not in ("pending", "active"):
        return
    store.update("cw_hires", hire_id, None, {"status": "active", "paid": int(paid), "subscription_id": subscription_id,
                                             "started_at": hire.get("started_at") or iso(), "updated_at": iso()})
    buyer = int(hire["buyer_id"])
    coworker = store.get_coworker(buyer) or {}
    store.update_coworker(buyer, settings={**(coworker.get("settings") or {}), "active_hire_id": hire_id})
    listing = store.get("cw_listings", int(hire["listing_id"])) or {}
    store.log(buyer, "marketplace", f"Hired “{listing.get('title', 'an AI')}”. Your engineer and reviewer now work from its knowledge.")
    store.log(int(hire["creator_id"]), "marketplace", f"Someone hired “{listing.get('title', 'your AI')}”")


def _end_hire(store: Store, hire: dict[str, Any], reason: str) -> None:
    store.update("cw_hires", hire["id"], None, {"status": "ended", "ended_at": iso(), "updated_at": iso()})
    buyer = int(hire["buyer_id"])
    coworker = store.get_coworker(buyer) or {}
    settings = dict(coworker.get("settings") or {})
    if settings.get("active_hire_id") == hire["id"]:
        settings.pop("active_hire_id")
        store.update_coworker(buyer, settings=settings)
    store.log(buyer, "marketplace", f"A hire ended: {reason}")
    if hire.get("subscription_id") and os.environ.get("STRIPE_SECRET_KEY"):
        try:
            _stripe().Subscription.delete(hire["subscription_id"])
        except Exception:  # Stripe may already have cancelled it; the hire is ended either way
            pass


def end(store: Store, buyer_id: int, hire_id: int) -> None:
    hire = store.get("cw_hires", hire_id)
    if not hire or int(hire["buyer_id"]) != buyer_id or hire["status"] not in ("active", "pending"):
        raise MarketError("No such active hire", "not_found")
    _end_hire(store, hire, "You ended it.")


def apply_checkout(store: Store, metadata: dict[str, Any], session: dict[str, Any]) -> None:
    """Stripe webhook: the buyer paid."""
    activate(store, int(metadata["hire_id"]), paid=True, subscription_id=str(session.get("subscription") or ""))


def apply_subscription_ended(store: Store, subscription: dict[str, Any]) -> None:
    hire_id = (subscription.get("metadata") or {}).get("hire_id")
    hire = store.get("cw_hires", int(hire_id)) if hire_id else None
    if hire and hire["status"] in ("active", "pending"):
        _end_hire(store, {**hire, "subscription_id": ""}, "The subscription ended.")


def hired_pack(store: Store, buyer_id: int) -> dict[str, Any] | None:
    """The pack the buyer's AI works from while a hire is active, else None."""
    hire_id = ((store.get_coworker(buyer_id) or {}).get("settings") or {}).get("active_hire_id")
    if not hire_id:
        return None
    hire = store.get("cw_hires", int(hire_id))
    if not hire or hire["status"] != "active":
        return None
    listing = store.get("cw_listings", int(hire["listing_id"]))
    return (listing or {}).get("pack") if listing and listing["status"] == "published" else None


# -- creators ---------------------------------------------------------------------------

def connect_payouts(store: Store, user_id: int) -> dict[str, Any]:
    """Start (or resume) Stripe Connect onboarding for the creator."""
    if not os.environ.get("STRIPE_SECRET_KEY"):
        raise MarketError("Payments aren't configured on this server", "not_configured")
    stripe = _stripe()
    coworker = store.get_coworker(user_id) or {}
    settings = dict(coworker.get("settings") or {})
    account = (settings.get("connect") or {}).get("account_id")
    if not account:
        acct = stripe.Account.create(type="express", email=coworker.get("owner_email") or None,
                                     metadata={"user_id": str(user_id)})
        account = acct["id"] if isinstance(acct, dict) else acct.id
        settings["connect"] = {"account_id": account}
        store.update_coworker(user_id, settings=settings)
    base = os.environ.get("FRONTEND_URL", "http://localhost:3000").rstrip("/")
    link = stripe.AccountLink.create(account=account, type="account_onboarding",
                                     refresh_url=f"{base}/app/coworker/marketplace?payouts=refresh",
                                     return_url=f"{base}/app/coworker/marketplace?payouts=done")
    return {"url": link["url"] if isinstance(link, dict) else link.url}


def earnings(store: Store, user_id: int) -> dict[str, Any]:
    """What the creator sees: hires and earnings, never buyers' data."""
    listing = store.one("SELECT * FROM cw_listings WHERE user_id = %s", (user_id,))
    if not listing:
        return {"listing": None}
    hires = store.query("SELECT status, paid, price_usd, creator_share FROM cw_hires WHERE listing_id = %s", (listing["id"],))
    active = [h for h in hires if h["status"] == "active"]
    monthly = sum(h["price_usd"] * float(h["creator_share"]) for h in active if h.get("paid"))
    return {"listing": profile(store, listing), "activeHires": len(active), "totalHires": len(hires),
            "monthlyEarningsUsd": round(monthly, 2), "share": creator_share(),
            "payoutsConnected": bool((((store.get_coworker(user_id) or {}).get("settings") or {}).get("connect") or {}).get("account_id"))}


def my_hires(store: Store, buyer_id: int) -> list[dict[str, Any]]:
    rows = store.query("SELECT * FROM cw_hires WHERE buyer_id = %s ORDER BY id DESC", (buyer_id,))
    out = []
    for h in rows:
        listing = store.get("cw_listings", int(h["listing_id"])) or {}
        out.append({"id": h["id"], "status": h["status"], "paid": bool(h.get("paid")), "priceUsd": h["price_usd"],
                    "slug": listing.get("slug", ""), "title": listing.get("title", ""), "startedAt": h.get("started_at")})
    return out


# -- reviews and reports -------------------------------------------------------------------

def rate(store: Store, buyer_id: int, slug: str, rating: int, text: str = "") -> None:
    listing = published(store, slug)
    if not store.one("SELECT id FROM cw_hires WHERE buyer_id = %s AND listing_id = %s AND status IN ('active', 'ended')",
                     (buyer_id, listing["id"])):
        raise MarketError("Only people who hired this AI can rate it", "forbidden")
    if not 1 <= int(rating) <= 5:
        raise MarketError("Rate from 1 to 5")
    if store.one("SELECT id FROM cw_listing_reviews WHERE listing_id = %s AND buyer_id = %s", (listing["id"], buyer_id)):
        raise MarketError("You've already rated this AI", "conflict")
    store.insert("cw_listing_reviews", {"listing_id": listing["id"], "buyer_id": buyer_id, "rating": int(rating),
                                        "text": text.strip()[:1000], "created_at": iso()})


def report(store: Store, reporter_id: int, slug: str, reason: str) -> None:
    listing = store.one("SELECT id, user_id, title FROM cw_listings WHERE slug = %s", (slug,))
    if not listing:
        raise MarketError("No such AI", "not_found")
    reason = reason.strip()[:1000]
    if not reason:
        raise MarketError("Tell us what's wrong")
    store.insert("cw_listing_reports", {"listing_id": listing["id"], "reporter_id": reporter_id, "reason": reason,
                                        "created_at": iso()})
    import observability

    observability.alert(f"marketplace-report:{listing['id']}", f"Listing reported: {listing['title']}", reason=reason[:200])


def reports(store: Store) -> list[dict[str, Any]]:
    return store.query("SELECT r.*, l.slug, l.title FROM cw_listing_reports r JOIN cw_listings l ON l.id = r.listing_id "
                       "ORDER BY r.id DESC LIMIT 200")


def serialize_listing(row: dict[str, Any]) -> dict[str, Any]:
    return {"id": row["id"], "slug": row["slug"], "title": row["title"], "headline": row.get("headline") or "",
            "role": row["role"], "priceUsd": row["price_usd"], "packVersion": row["pack_version"], "status": row["status"]}
