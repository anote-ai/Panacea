"""SSE streaming helpers for agent and LLM responses."""
from __future__ import annotations

import json
import os
from collections.abc import Callable, Generator

from services.llm import get_provider_for_model
from services.provider_keys import get_user_provider_key

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


def _require_api_key(provider: str, user_id: int | None = None) -> str:
    if provider == "ollama":
        return ""
    if user_id is not None:
        user_key = get_user_provider_key(user_id, provider)
        if user_key:
            return user_key
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
    user_id: int | None = None,
) -> Generator[str, None, None]:
    """Stream an agent response via SSE, routed to the provider for `model`.

    `on_text` is invoked with each text delta as it streams, so callers can
    accumulate the full reply for persistence without re-parsing SSE frames.
    `user_id`, if given, is checked first for a user-supplied provider key
    before falling back to the server's env-configured key.
    """
    provider = get_provider_for_model(model)
    try:
        api_key = _require_api_key(provider, user_id)
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
        elif provider == "google":
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            gm = genai.GenerativeModel(model)
            for chunk in gm.generate_content(message, stream=True):
                text = chunk.text
                if text:
                    if on_text:
                        on_text(text)
                    yield _sse("text", {"text": text})
        elif provider == "ollama":
            import requests
            base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
            with requests.post(
                f"{base_url}/api/generate",
                json={"model": model, "prompt": message, "stream": True},
                stream=True,
                timeout=120,
            ) as resp:
                resp.raise_for_status()
                for line in resp.iter_lines():
                    if not line:
                        continue
                    chunk = json.loads(line)
                    text = chunk.get("response", "")
                    if text:
                        if on_text:
                            on_text(text)
                        yield _sse("text", {"text": text})
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
    user_id: int | None = None,
) -> str:
    """Non-streaming LLM completion, routed to the provider for `model`."""
    history = history or []
    provider = get_provider_for_model(model)
    api_key = _require_api_key(provider, user_id)
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
    if provider == "google":
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        gm = genai.GenerativeModel(model)
        gm_history = [
            {"role": "model" if h.get("role") == "assistant" else "user", "parts": [h["content"]]}
            for h in history
        ]
        chat = gm.start_chat(history=gm_history)
        return chat.send_message(message).text or ""
    if provider == "ollama":
        import requests
        base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        messages = [*history, {"role": "user", "content": message}]
        resp = requests.post(
            f"{base_url}/api/chat",
            json={"model": model, "messages": messages, "stream": False},
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json().get("message", {}).get("content", "")
    raise RuntimeError(f"Streaming is not supported for provider '{provider}'")
