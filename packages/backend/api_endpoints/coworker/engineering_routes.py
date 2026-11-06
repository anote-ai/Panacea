"""Knowledge packs, the AI engineer, and the AI code reviewer."""
from __future__ import annotations

from typing import Any

from flask import jsonify, request

from api_endpoints.coworker.common import coworker_bp, error, store, uid
from coworker import knowledge_pack
from coworker.connectors.base import ConnectorError
from coworker.engineering import review, runs
from middleware.auth import require_auth


def _body() -> dict[str, Any]:
    return request.get_json(silent=True) or {}


def _need_coworker() -> tuple | None:
    if not store().get_coworker(uid()):
        return error("Set up your coworker first", 404, "not_found")
    return None


def _run_error(exc: runs.RunError | ConnectorError) -> tuple:
    status = {"not_found": 404, "conflict": 409, "needs_model": 409, "not_connected": 409, "plan_limit": 402}.get(exc.code, 400)
    return error(str(exc), status, exc.code)


# -- knowledge pack ----------------------------------------------------------------

@coworker_bp.get("/knowledge-pack")
@require_auth
def get_pack() -> tuple:
    if (missing := _need_coworker()) is not None:
        return missing
    row = knowledge_pack.draft(store(), uid()) or knowledge_pack.build(store(), uid())
    return jsonify(knowledge_pack.serialize(row)), 200


@coworker_bp.post("/knowledge-pack/build")
@require_auth
def build_pack() -> tuple:
    if (missing := _need_coworker()) is not None:
        return missing
    return jsonify(knowledge_pack.serialize(knowledge_pack.build(store(), uid()))), 200


@coworker_bp.patch("/knowledge-pack")
@require_auth
def edit_pack() -> tuple:
    data = _body()
    if (missing := _need_coworker()) is not None:
        return missing
    try:
        row = knowledge_pack.edit(store(), uid(), str(data.get("section", "")), str(data.get("op", "")),
                                  str(data.get("id", "")), data.get("values") or {})
    except ValueError as exc:
        return error(str(exc))
    return jsonify(knowledge_pack.serialize(row)), 200


@coworker_bp.get("/knowledge-pack/versions")
@require_auth
def pack_versions() -> tuple:
    return jsonify({"versions": [{"version": v["version"], "sources": v.get("sources") or [], "createdAt": v["created_at"]}
                                 for v in knowledge_pack.versions(store(), uid())]}), 200


@coworker_bp.post("/knowledge-pack/versions")
@require_auth
def freeze_pack() -> tuple:
    if (missing := _need_coworker()) is not None:
        return missing
    return jsonify(knowledge_pack.serialize(knowledge_pack.freeze(store(), uid()))), 201


# -- AI engineer ---------------------------------------------------------------------

@coworker_bp.get("/engineer/runs")
@require_auth
def list_engineer_runs() -> tuple:
    return jsonify({"runs": [runs.serialize(r) for r in runs.runs(store(), uid())]}), 200


@coworker_bp.post("/engineer/runs")
@require_auth
def create_engineer_run() -> tuple:
    data = _body()
    if (missing := _need_coworker()) is not None:
        return missing
    try:
        run = runs.create(store(), uid(), text=str(data.get("text", ""))[:20000], source=str(data.get("source", "")),
                          repo=str(data.get("repo", "")))
    except (runs.RunError, ConnectorError) as exc:
        return _run_error(exc)
    return jsonify(runs.serialize(run)), 201


@coworker_bp.get("/engineer/runs/<int:run_id>")
@require_auth
def get_engineer_run(run_id: int) -> tuple:
    run = store().get("cw_eng_runs", run_id, uid())
    if not run:
        return error("No such run", 404, "not_found")
    return jsonify(runs.serialize(run)), 200


@coworker_bp.patch("/engineer/runs/<int:run_id>/spec")
@require_auth
def edit_spec(run_id: int) -> tuple:
    try:
        return jsonify(runs.serialize(runs.update_spec(store(), uid(), run_id, _body()))), 200
    except runs.RunError as exc:
        return _run_error(exc)


@coworker_bp.post("/engineer/runs/<int:run_id>/plan")
@require_auth
def plan_engineer_run(run_id: int) -> tuple:
    try:
        return jsonify(runs.serialize(runs.plan(store(), uid(), run_id))), 200
    except (runs.RunError, ConnectorError) as exc:
        return _run_error(exc)


@coworker_bp.patch("/engineer/runs/<int:run_id>/graph")
@require_auth
def edit_graph(run_id: int) -> tuple:
    nodes = _body().get("nodes")
    if not isinstance(nodes, list):
        return error("Send the task list as nodes")
    try:
        return jsonify(runs.serialize(runs.update_graph(store(), uid(), run_id, nodes))), 200
    except runs.RunError as exc:
        return _run_error(exc)


@coworker_bp.post("/engineer/runs/<int:run_id>/start")
@require_auth
def start_engineer_run(run_id: int) -> tuple:
    try:
        return jsonify(runs.serialize(runs.start(store(), uid(), run_id))), 202
    except (runs.RunError, ConnectorError) as exc:
        return _run_error(exc)


# -- AI code reviewer ----------------------------------------------------------------

@coworker_bp.get("/reviews")
@require_auth
def list_reviews() -> tuple:
    rows = store().query("SELECT * FROM cw_reviews WHERE user_id = %s ORDER BY id DESC LIMIT 50", (uid(),))
    return jsonify({"reviews": [review.serialize(r) for r in rows]}), 200


@coworker_bp.post("/reviews")
@require_auth
def review_pr() -> tuple:
    data = _body()
    repo, number = str(data.get("repo", "")).strip(), data.get("number")
    if repo.count("/") != 1 or not str(number).isdigit():
        return error("Give the repository (owner/name) and the pull request number")
    if (missing := _need_coworker()) is not None:
        return missing
    try:
        row = review.review_pull_request(store(), uid(), repo, int(str(number)))
    except ConnectorError as exc:
        return _run_error(exc)
    return jsonify(review.serialize(row)), 201


@coworker_bp.get("/reviews/<int:review_id>")
@require_auth
def get_review(review_id: int) -> tuple:
    row = store().get("cw_reviews", review_id, uid())
    if not row:
        return error("No such review", 404, "not_found")
    return jsonify(review.serialize(row)), 200


@coworker_bp.post("/reviews/<int:review_id>/findings/<path:finding_id>/dismiss")
@require_auth
def dismiss_finding(review_id: int, finding_id: str) -> tuple:
    scope = str(_body().get("scope", "once"))
    if scope not in ("once", "repo", "everywhere"):
        return error("scope is once, repo, or everywhere")
    try:
        row = review.dismiss(store(), uid(), review_id, finding_id, scope)
    except LookupError as exc:
        return error(str(exc), 404, "not_found")
    return jsonify(review.serialize(row)), 200
