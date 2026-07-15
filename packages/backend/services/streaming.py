"""SSE streaming helpers for agent and LLM responses."""
from __future__ import annotations

import json
import os
from collections.abc import Callable, Generator

from services.llm import get_provider_for_model

_ENV_KEY_FOR_PROVIDER = {
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
    "google": "GEMINI_API_KEY",
}


def sse_event(event: str, data: dict) -> str:  # type: ignore[type-arg]
    # The frontend reads `type` from the JSON payload itself (it doesn't parse
    # the SSE `event:` line), so every payload must carry it too.
    payload = {"type": event, **data}
    return f"event: {event}\ndata: {json.dumps(payload)}\n\n"


_sse = sse_event


def _require_api_key(provider: str) -> str:
    env_key = _ENV_KEY_FOR_PROVIDER.get(provider)
    if not env_key:
        raise RuntimeError(f"Streaming is not supported for provider '{provider}'")
    api_key = os.environ.get(env_key, "")
    if not api_key:
        raise RuntimeError(f"{env_key} not configured")
    return api_key


def stream_agent_response(
    message: str,
    cwd: str = ".",
    model: str = "claude-sonnet-4-6",
    on_text: Callable[[str], None] | None = None,
) -> Generator[str, None, None]:
    """Stream an agent response via SSE, routed to the provider for `model`.

    `on_text` is invoked with each text delta as it streams, so callers can
    accumulate the full reply for persistence without re-parsing SSE frames.
    """
    provider = get_provider_for_model(model)
    try:
        api_key = _require_api_key(provider)
    except RuntimeError as exc:
        yield _sse("error", {"message": str(exc)})
        return
    try:
        if provider == "anthropic":
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            with client.messages.stream(
                model=model,
                max_tokens=4096,
                messages=[{"role": "user", "content": message}],  # type: ignore[list-item]
            ) as stream:
                for text in stream.text_stream:
                    if on_text:
                        on_text(text)
                    yield _sse("text", {"text": text})
        elif provider == "openai":
            from openai import OpenAI
            client_oa = OpenAI(api_key=api_key)
            oa_stream = client_oa.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": message}],  # type: ignore[list-item]
                max_tokens=4096,
                stream=True,
            )
            for chunk in oa_stream:
                delta = chunk.choices[0].delta.content if chunk.choices else None
                if delta:
                    if on_text:
                        on_text(delta)
                    yield _sse("text", {"text": delta})
        else:
            yield _sse("error", {"message": f"Streaming is not supported for provider '{provider}'"})
            return
        yield _sse("done", {})
    except Exception as exc:
        yield _sse("error", {"message": str(exc)})


def stream_llm_response(
    message: str,
    model: str = "claude-sonnet-4-6",
    history: list[dict] | None = None,  # type: ignore[type-arg]
) -> str:
    """Non-streaming LLM completion, routed to the provider for `model`."""
    history = history or []
    provider = get_provider_for_model(model)
    api_key = _require_api_key(provider)
    if provider == "anthropic":
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
    if provider == "openai":
        from openai import OpenAI
        client_oa = OpenAI(api_key=api_key)
        messages_oa = [*history, {"role": "user", "content": message}]
        response_oa = client_oa.chat.completions.create(
            model=model,
            messages=messages_oa,  # type: ignore[arg-type]
            max_tokens=4096,
        )
        choice = response_oa.choices[0] if response_oa.choices else None
        return (choice.message.content or "") if choice else ""
    raise RuntimeError(f"Streaming is not supported for provider '{provider}'")
