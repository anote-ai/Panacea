"""API usage metering — deduct credits and log token usage per request.

Ported from the standalone root-level backend/database/usage.py: a flat
1 credit is charged per completed chat request regardless of token count;
token counts are stored purely for display in the Usage settings tab.
"""
from __future__ import annotations


def record_usage(
    user_id: int | None,
    endpoint: str,
    model: str | None,
    prompt_tokens: int,
    completion_tokens: int,
    credits_used: int = 1,
) -> None:
    """Deduct credits and log the request. Never raises — usage metering
    is best-effort and must never break a user-facing chat response."""
    if user_id is None:
        return
    from database.db import deduct_credits, get_connection, log_api_usage

    try:
        cnx = get_connection()
        try:
            deduct_credits(cnx, user_id, credits_used)
            log_api_usage(cnx, user_id, endpoint, model, prompt_tokens, completion_tokens, credits_used)
            cnx.commit()
        finally:
            cnx.close()
    except Exception as exc:
        print(f"[usage] record_usage failed: {exc}")
