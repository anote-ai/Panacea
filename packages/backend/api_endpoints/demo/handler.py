"""Public no-auth demo endpoints: pre-loaded sample documents + limited Q&A (issue #200)."""
from __future__ import annotations

from flask import Blueprint, jsonify, request

from services.demo import DEMO_DOCS, answer_demo_question, ensure_indexed

demo_bp = Blueprint("demo", __name__, url_prefix="/api/demo")

QUESTION_LIMIT = 5

# Per-client question counts, keyed by IP. In-memory by design: the demo gate
# is a soft conversion nudge, not a security boundary.
_question_counts: dict[str, int] = {}

_DEMO_DOC_IDS = {doc["id"] for doc in DEMO_DOCS}


def _client_key() -> str:
    forwarded = request.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr or "unknown"


@demo_bp.get("/documents")
def list_demo_documents() -> tuple:  # type: ignore[type-arg]
    """The pre-loaded sample documents, plus the caller's remaining free questions."""
    remaining = max(0, QUESTION_LIMIT - _question_counts.get(_client_key(), 0))
    docs = [
        {
            "id": doc["id"],
            "name": doc["name"],
            "category": doc["category"],
            "suggestedQuestions": doc["suggestedQuestions"],
        }
        for doc in DEMO_DOCS
    ]
    return jsonify({"documents": docs, "questionLimit": QUESTION_LIMIT, "remaining": remaining}), 200


@demo_bp.post("/ask")
def ask_demo() -> tuple:  # type: ignore[type-arg]
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()
    if not question:
        return jsonify({"error": "Question is required"}), 400
    if len(question) > 500:
        return jsonify({"error": "Question is too long (500 characters max)"}), 400

    doc_id = data.get("docId") or None
    if doc_id is not None and doc_id not in _DEMO_DOC_IDS:
        return jsonify({"error": "Unknown demo document"}), 404

    key = _client_key()
    used = _question_counts.get(key, 0)
    if used >= QUESTION_LIMIT:
        return (
            jsonify({
                "error": "Free demo limit reached — sign up to keep asking questions.",
                "signupRequired": True,
                "remaining": 0,
            }),
            429,
        )

    try:
        ensure_indexed()
        result = answer_demo_question(question, doc_id)
    except Exception:
        return jsonify({"error": "Internal server error"}), 500

    _question_counts[key] = used + 1
    return (
        jsonify({
            "answer": result["answer"],
            "sources": result["sources"],
            "remaining": QUESTION_LIMIT - (used + 1),
        }),
        200,
    )
