"""The output scorecard: work done per unit of time, per AI and per team."""
from __future__ import annotations

from flask import Response, jsonify, request

from api_endpoints.coworker.common import coworker_bp, error, store, uid
from coworker import scorecard
from middleware.auth import require_auth


def _days() -> int:
    try:
        return max(1, min(int(request.args.get("days", 7)), 365))
    except ValueError:
        return 7


@coworker_bp.get("/scorecard")
@require_auth
def get_scorecard() -> tuple | Response:
    s = store()
    if not s.get_coworker(uid()):
        return error("Set up your coworker first", 404, "not_found")
    scorecard.refresh_merged(s, uid())
    data = scorecard.card(s, uid(), _days())
    if request.args.get("format") == "csv":
        return Response(scorecard.to_csv(data), mimetype="text/csv",
                        headers={"Content-Disposition": f"attachment; filename=scorecard-{data['days']}d.csv"})
    return jsonify(data), 200


@coworker_bp.get("/team/scorecard")
@require_auth
def get_team_scorecard() -> tuple:
    data = scorecard.team(store(), uid(), _days())
    if data is None:
        return error("Only organization admins can see the team scorecard", 403, "forbidden")
    return jsonify(data), 200
