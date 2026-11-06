"""The one-month trial hire, and the operator view of every trial."""
from __future__ import annotations

from typing import Any

from flask import jsonify, request

from api_endpoints.coworker.common import coworker_bp, error, store, uid
from coworker import trial
from middleware.auth import require_auth

STATUS = {"not_found": 404, "conflict": 409, "bad_request": 400}


def _body() -> dict[str, Any]:
    return request.get_json(silent=True) or {}


def _fail(exc: trial.TrialError) -> tuple:
    return error(str(exc), STATUS.get(exc.code, 400), exc.code)


def _view(row: dict[str, Any]) -> dict[str, Any]:
    return {**trial.serialize(row), "progress": trial.progress(store(), uid(), row)}


@coworker_bp.get("/trial")
@require_auth
def get_trial() -> tuple:
    row = trial.current(store(), uid())
    return jsonify({"trial": _view(row) if row else None, "defaults": trial.DEFAULT_GOALS,
                    "metrics": trial.METRICS, "guarantee": trial.GUARANTEE}), 200


@coworker_bp.post("/trial")
@require_auth
def start_trial() -> tuple:
    data = _body()
    try:
        row = trial.start(store(), uid(), str(data.get("role", "")), data.get("goals"), str(data.get("approver", "")))
    except trial.TrialError as exc:
        return _fail(exc)
    return jsonify({"trial": _view(row)}), 201


@coworker_bp.put("/trial/goals")
@require_auth
def set_trial_goals() -> tuple:
    goals = _body().get("goals")
    if not isinstance(goals, list):
        return error("Send the goals as a list")
    try:
        return jsonify({"trial": _view(trial.update_goals(store(), uid(), goals))}), 200
    except trial.TrialError as exc:
        return _fail(exc)


@coworker_bp.post("/trial/decide")
@require_auth
def decide_trial() -> tuple:
    data = _body()
    choice = str(data.get("choice", ""))
    try:
        row = trial.decide(store(), uid(), choice, str(data.get("plan", "coworker")))
    except trial.TrialError as exc:
        return _fail(exc)
    out: dict[str, Any] = {"trial": _view(row)}
    if choice == "convert":
        from coworker import billing

        try:
            out["billing"] = billing.change_plan(store(), uid(), str(data.get("plan", "coworker")))
        except billing.PlanError as exc:
            out["billing"] = {"status": "error", "error": str(exc)}
    return jsonify(out), 200


# -- operators ----------------------------------------------------------------------

@coworker_bp.get("/operator/trials")
@require_auth
def operator_trials() -> tuple:
    if not trial.is_operator(store(), uid()):
        return error("Operators only", 403, "forbidden")
    return jsonify({"trials": trial.operator_overview(store())}), 200


@coworker_bp.get("/operator/trials/<int:trial_id>")
@require_auth
def operator_trial(trial_id: int) -> tuple:
    if not trial.is_operator(store(), uid()):
        return error("Operators only", 403, "forbidden")
    row = store().get("cw_trials", trial_id)
    if not row:
        return error("No such trial", 404, "not_found")
    owner = int(row["user_id"])
    return jsonify({**trial.serialize(row), "progress": trial.progress(store(), owner, row),
                    "flags": trial.flagged(store(), owner),
                    "activity": store().activity(owner, limit=50)}), 200


@coworker_bp.post("/operator/trials/<int:trial_id>/notes")
@require_auth
def operator_note(trial_id: int) -> tuple:
    if not trial.is_operator(store(), uid()):
        return error("Operators only", 403, "forbidden")
    try:
        return jsonify(trial.operator_note(store(), uid(), trial_id, str(_body().get("text", "")))), 201
    except trial.TrialError as exc:
        return _fail(exc)


@coworker_bp.get("/operator/pricing")
@require_auth
def operator_pricing() -> tuple:
    """The margin analysis behind the plan lineups (operators only)."""
    if not trial.is_operator(store(), uid()):
        return error("Operators only", 403, "forbidden")
    from coworker import pricing

    return jsonify(pricing.analyze(store())), 200


# -- API tokens (session only: a token can't manage tokens) ------------------------------

@coworker_bp.get("/tokens")
@require_auth
def list_tokens() -> tuple:
    from coworker import api_tokens

    return jsonify({"tokens": api_tokens.listing(store(), uid()), "allowed": [
        f"{m} /api/coworker{p.pattern.strip('^$')}" for m, p in api_tokens.ALLOWED]}), 200


@coworker_bp.post("/tokens")
@require_auth
def create_token() -> tuple:
    from coworker import api_tokens

    try:
        row, token = api_tokens.create(store(), uid(), str(_body().get("name", "")))
    except ValueError as exc:
        return error(str(exc), 409, "conflict")
    return jsonify({"id": row["id"], "name": row["name"], "token": token,
                    "note": "Copy it now: it won't be shown again."}), 201


@coworker_bp.delete("/tokens/<int:token_id>")
@require_auth
def revoke_token(token_id: int) -> tuple:
    from coworker import api_tokens

    if not api_tokens.revoke(store(), uid(), token_id):
        return error("No such token", 404, "not_found")
    return jsonify({"revoked": True}), 200
