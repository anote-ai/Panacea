"""Chat endpoints — SSE streaming agent chat and session management."""
from __future__ import annotations

import os
from collections.abc import Generator

from flask import Blueprint, Response, jsonify, request, stream_with_context
from flask_jwt_extended import get_jwt_identity

from database.db import (
    create_chat,
    create_message,
    get_chat,
    get_chats,
    get_connection,
    get_messages,
    rename_chat,
)
from database.db import delete_chat as db_delete_chat
from middleware.auth import require_auth
from services.streaming import sse_event, stream_agent_response, stream_llm_response
from services.titles import generate_chat_title

chat_bp = Blueprint("chat", __name__, url_prefix="/api/chat")


@chat_bp.post("/stream")
@require_auth
def chat_stream() -> Response:
    """SSE endpoint: stream an agent response and persist the exchange."""
    data = request.get_json(silent=True) or {}
    message: str = data.get("message", "").strip()
    cwd: str = data.get("cwd", os.getcwd())
    model: str = data.get("model", "claude-sonnet-4-6")
    session_id_raw = data.get("session_id")

    if not message:
        return jsonify({"error": "message is required"}), 400  # type: ignore[return-value]

    user_id = int(get_jwt_identity())

    is_new_chat = not session_id_raw
    cnx = get_connection()
    try:
        if is_new_chat:
            chat_id: int = create_chat(cnx, user_id)
            needs_title = True
        else:
            chat_id = int(session_id_raw)  # type: ignore[arg-type]
            chat_row = get_chat(cnx, user_id, chat_id)
            if not chat_row:
                return jsonify({"error": "Session not found"}), 404  # type: ignore[return-value]
            # A prior attempt on this chat may have failed before ever
            # producing a reply, leaving the default name in place — retry
            # title generation in that case instead of only on creation.
            needs_title = chat_row["name"] == "New Chat"
        create_message(cnx, chat_id, "user", message)
    finally:
        cnx.close()

    def generate() -> Generator[str, None, None]:
        if is_new_chat:
            yield sse_event("session_id", {"session_id": chat_id})

        accumulated_parts: list[str] = []
        yield from stream_agent_response(
            message=message, cwd=cwd, model=model, on_text=accumulated_parts.append,
        )
        accumulated = "".join(accumulated_parts)

        if accumulated:
            cnx2 = get_connection()
            try:
                create_message(cnx2, chat_id, "assistant", accumulated, model)
                if needs_title:
                    title = generate_chat_title(message, accumulated, model=model)
                    rename_chat(cnx2, user_id, chat_id, title)
                    yield sse_event("title", {"session_id": chat_id, "title": title})
            finally:
                cnx2.close()

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@chat_bp.post("")
def chat() -> tuple:
    """Non-streaming chat completion."""
    data = request.get_json(silent=True) or {}
    message: str = data.get("message", "").strip()
    model: str = data.get("model", "claude-sonnet-4-6")
    history: list[dict] = data.get("history", [])

    if not message:
        return jsonify({"error": "message is required"}), 400

    try:
        response_text = stream_llm_response(message=message, model=model, history=history)
        return jsonify({"response": response_text, "model": model}), 200
    except Exception as exc:
        print(f"Chat error: {exc}")
        return jsonify({"error": "Internal server error"}), 500


@chat_bp.get("/sessions")
@require_auth
def list_sessions() -> tuple:
    user_id = int(get_jwt_identity())
    cnx = get_connection()
    try:
        chats = get_chats(cnx, user_id)
    finally:
        cnx.close()
    sessions = [
        {"id": str(c["id"]), "title": c["name"], "createdAt": c["created_at"].isoformat()}
        for c in chats
    ]
    return jsonify({"sessions": sessions}), 200


@chat_bp.get("/sessions/<int:chat_id>")
@require_auth
def get_session(chat_id: int) -> tuple:
    user_id = int(get_jwt_identity())
    cnx = get_connection()
    try:
        chat_row = get_chat(cnx, user_id, chat_id)
        if not chat_row:
            return jsonify({"error": "Session not found"}), 404
        messages = get_messages(cnx, chat_id)
    finally:
        cnx.close()
    return jsonify({
        "sessionId": str(chat_id),
        "messages": [
            {"role": m["role"], "content": m["content"], "createdAt": m["created_at"].isoformat()}
            for m in messages
        ],
    }), 200


@chat_bp.delete("/sessions/<int:chat_id>")
@require_auth
def delete_session(chat_id: int) -> tuple:
    user_id = int(get_jwt_identity())
    cnx = get_connection()
    try:
        db_delete_chat(cnx, user_id, chat_id)
    finally:
        cnx.close()
    return jsonify({"deleted": True}), 200
