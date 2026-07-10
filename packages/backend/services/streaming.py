"""SSE streaming helpers for agent and LLM responses."""
from __future__ import annotations

import json
import os
from collections.abc import Callable, Generator


def sse_event(event: str, data: dict) -> str:  # type: ignore[type-arg]
    """Format an SSE event with a client-friendly type field."""
    payload = {"type": event, **data}
    return f"event: {event}\ndata: {json.dumps(payload)}\n\n"


_sse = sse_event


def stream_agent_response(
    message: str,
    cwd: str = ".",
    model: str = "claude-sonnet-4-6",
    history: list[dict] | None = None,  # type: ignore[type-arg]
    on_text: Callable[[str], None] | None = None,
) -> Generator[str, None, None]:
    """Stream an agent response via SSE using the Anthropic SDK."""
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        yield _sse("error", {"message": "ANTHROPIC_API_KEY not configured"})
        return
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        with client.messages.stream(
            model=model,
            max_tokens=4096,
            messages=[*(history or []), {"role": "user", "content": message}],  # type: ignore[list-item]
        ) as stream:
            for text in stream.text_stream:
                if on_text:
                    on_text(text)
                yield _sse("text", {"text": text})
        yield _sse("done", {})
    except Exception as exc:
        yield _sse("error", {"message": str(exc)})


def stream_llm_response(
    message: str,
    model: str = "claude-sonnet-4-6",
    history: list[dict] | None = None,  # type: ignore[type-arg]
) -> str:
    """Non-streaming LLM completion."""
    history = history or []
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not configured")
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    messages = [*history, {"role": "user", "content": message}]
    response = client.messages.create(
        model=model,
        max_tokens=4096,
        messages=messages,  # type: ignore[arg-type]
    )
    block = response.content[0] if response.content else None
    return block.text if block and hasattr(block, "text") else ""  # type: ignore[union-attr]
