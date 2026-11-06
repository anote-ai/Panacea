"""The marketplace: public AI profiles, publishing, hiring, ratings, reports."""
from __future__ import annotations

from typing import Any

from flask import jsonify, request

from api_endpoints.coworker.common import coworker_bp, error, store, uid
from coworker import knowledge_pack, marketplace, trial
from middleware.auth import require_auth

STATUS = {"not_found": 404, "conflict": 409, "forbidden": 403, "not_configured": 501}


def _body() -> dict[str, Any]:
    return request.get_json(silent=True) or {}


def _fail(exc: marketplace.MarketError) -> tuple:
    return error(str(exc), STATUS.get(exc.code, 400), exc.code)


# -- public ------------------------------------------------------------------------------

@coworker_bp.get("/marketplace")
def market_directory() -> tuple:
    return jsonify({"listings": marketplace.directory(store(), request.args.get("role", ""),
                                                     request.args.get("q", "")[:100])}), 200


@coworker_bp.get("/marketplace/ai/<slug>")
def market_profile(slug: str) -> tuple:
    try:
        return jsonify(marketplace.profile(store(), marketplace.published(store(), slug))), 200
    except marketplace.MarketError as exc:
        return _fail(exc)


# -- creators ------------------------------------------------------------------------------

@coworker_bp.get("/marketplace/me")
@require_auth
def market_me() -> tuple:
    s = store()
    return jsonify({**marketplace.earnings(s, uid()), "consent": marketplace.consent_text(s, uid()),
                    "versions": [v["version"] for v in knowledge_pack.versions(s, uid())],
                    "hires": marketplace.my_hires(s, uid()), "share": marketplace.creator_share(),
                    "roles": list(marketplace.ROLES)}), 200


@coworker_bp.post("/marketplace/publish")
@require_auth
def market_publish() -> tuple:
    d = _body()
    try:
        row = marketplace.publish(store(), uid(), version=int(d.get("version") or 0), title=str(d.get("title", "")),
                                  headline=str(d.get("headline", "")), role=str(d.get("role", "")),
                                  price_usd=int(d.get("priceUsd") or 0), consent=str(d.get("consent", "")))
    except (ValueError, TypeError):
        return error("Version and price must be numbers")
    except marketplace.MarketError as exc:
        return _fail(exc)
    return jsonify(marketplace.serialize_listing(row)), 201


@coworker_bp.post("/marketplace/unpublish")
@require_auth
def market_unpublish() -> tuple:
    try:
        return jsonify(marketplace.serialize_listing(marketplace.unpublish(store(), uid()))), 200
    except marketplace.MarketError as exc:
        return _fail(exc)


@coworker_bp.post("/marketplace/payouts")
@require_auth
def market_payouts() -> tuple:
    try:
        return jsonify(marketplace.connect_payouts(store(), uid())), 200
    except marketplace.MarketError as exc:
        return _fail(exc)


# -- buyers ----------------------------------------------------------------------------------

@coworker_bp.post("/marketplace/ai/<slug>/hire")
@require_auth
def market_hire(slug: str) -> tuple:
    try:
        return jsonify(marketplace.hire(store(), uid(), slug)), 201
    except marketplace.MarketError as exc:
        return _fail(exc)


@coworker_bp.post("/marketplace/hires/<int:hire_id>/end")
@require_auth
def market_end_hire(hire_id: int) -> tuple:
    try:
        marketplace.end(store(), uid(), hire_id)
    except marketplace.MarketError as exc:
        return _fail(exc)
    return jsonify({"ended": True}), 200


@coworker_bp.post("/marketplace/ai/<slug>/rate")
@require_auth
def market_rate(slug: str) -> tuple:
    d = _body()
    try:
        marketplace.rate(store(), uid(), slug, int(d.get("rating") or 0), str(d.get("text", "")))
    except (ValueError, TypeError):
        return error("Rate from 1 to 5")
    except marketplace.MarketError as exc:
        return _fail(exc)
    return jsonify({"ok": True}), 201


@coworker_bp.post("/marketplace/ai/<slug>/report")
@require_auth
def market_report(slug: str) -> tuple:
    try:
        marketplace.report(store(), uid(), slug, str(_body().get("reason", "")))
    except marketplace.MarketError as exc:
        return _fail(exc)
    return jsonify({"ok": True}), 201


@coworker_bp.get("/operator/marketplace/reports")
@require_auth
def market_reports() -> tuple:
    if not trial.is_operator(store(), uid()):
        return error("Operators only", 403, "forbidden")
    return jsonify({"reports": marketplace.reports(store())}), 200
