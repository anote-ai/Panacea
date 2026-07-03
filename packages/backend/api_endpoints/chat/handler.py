"""Chat endpoints — SSE streaming agent chat and session management."""
from __future__ import annotations

import os
from collections.abc import Generator

from flask import Blueprint, Response, current_app, jsonify, request, stream_with_context

from services.chat_sessions import ChatSessionStore
from services.streaming import sse_event, stream_agent_response, stream_llm_response

chat_bp = Blueprint("chat", __name__, url_prefix="/api/chat")


def _store() -> ChatSessionStore:
    return ChatSessionStore(current_app.config["CHAT_SESSION_DB_PATH"])


def _title_from_message(message: str) -> str:
    first_line = " ".join(message.strip().splitlines()[0:1]).strip()
    if not first_line:
        return "New chat"
    return first_line[:77] + "..." if len(first_line) > 80 else first_line


def _model_history(messages: list[dict]) -> list[dict]:
    return [
        {"role": m["role"], "content": m["content"]}
        for m in messages
        if m.get("role") in {"user", "assistant"} and m.get("content")
    ]


@chat_bp.post("/stream")
def chat_stream() -> Response:
    """SSE endpoint: stream an agent response to the client."""
    data = request.get_json(silent=True) or {}
    message: str = data.get("message", "").strip()
    cwd: str = data.get("cwd", os.getcwd())
    model: str = data.get("model", "claude-sonnet-4-6")
    requested_session_id = data.get("session_id") or data.get("sessionId")

    if not message:
        return jsonify({"error": "message is required"}), 400  # type: ignore[return-value]

    store = _store()
    session = store.ensure_session(
        str(requested_session_id) if requested_session_id else None,
        title=_title_from_message(message),
        cwd=cwd,
        model=model,
    )
    session_id = session["id"]
    history = _model_history(store.get_messages(session_id))
    store.add_message(session_id, role="user", content=message, model=model)

    def generate() -> Generator[str, None, None]:
        assistant_parts: list[str] = []
        yield sse_event("session_id", {"session_id": session_id})
        yield from stream_agent_response(
            message=message,
            cwd=cwd,
            model=model,
            history=history,
            on_text=assistant_parts.append,
        )
        assistant_text = "".join(assistant_parts).strip()
        if assistant_text:
            store.add_message(session_id, role="assistant", content=assistant_text, model=model)

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
    requested_session_id = data.get("session_id") or data.get("sessionId")

    if not message:
        return jsonify({"error": "message is required"}), 400

    try:
        session_id = None
        store = _store()
        if requested_session_id:
            session = store.ensure_session(
                str(requested_session_id),
                title=_title_from_message(message),
                cwd=os.getcwd(),
                model=model,
            )
            session_id = session["id"]
            history = _model_history(store.get_messages(session_id))
        response_text = stream_llm_response(message=message, model=model, history=history)
        if session_id:
            store.add_message(session_id, role="user", content=message, model=model)
            store.add_message(session_id, role="assistant", content=response_text, model=model)
        return jsonify({"response": response_text, "model": model, "sessionId": session_id}), 200
    except Exception as exc:
        print(f"Chat error: {exc}")
        return jsonify({"error": "Internal server error"}), 500


@chat_bp.get("/sessions")
def list_sessions() -> tuple:
    return jsonify({"sessions": _store().list_sessions()}), 200


@chat_bp.post("/sessions")
def create_session() -> tuple:
    data = request.get_json(silent=True) or {}
    session = _store().create_session(
        title=data.get("title") or "New chat",
        cwd=data.get("cwd") or "",
        model=data.get("model") or "",
    )
    return jsonify({"sessionId": session["id"], "session": session}), 201


@chat_bp.get("/sessions/<session_id>")
def get_session(session_id: str) -> tuple:
    store = _store()
    session = store.get_session(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404
    return jsonify({
        "sessionId": session_id,
        "session": session,
        "messages": store.get_messages(session_id),
    }), 200


@chat_bp.get("/sessions/<session_id>/messages")
def get_session_messages(session_id: str) -> tuple:
    store = _store()
    if not store.get_session(session_id):
        return jsonify({"error": "Session not found"}), 404
    messages = store.get_messages(session_id)
    return jsonify({"sessionId": session_id, "history": messages, "messages": messages}), 200


@chat_bp.delete("/sessions/<session_id>")
def delete_session(session_id: str) -> tuple:
    deleted = _store().delete_session(session_id)
    return jsonify({"deleted": deleted, "ok": deleted}), 200
