"""Auto-generate short chat titles that summarize a conversation's topic."""
from __future__ import annotations

from services.llm import complete

_TITLE_SYSTEM_PROMPT = (
    "Generate a short title (3-6 words, no quotes, no trailing punctuation) "
    "summarizing the topic being discussed, based on the exchange below. "
    "Reply with only the title, nothing else."
)


def generate_chat_title(
    user_message: str,
    assistant_reply: str = "",
    model: str = "claude-sonnet-4-6",
) -> str:
    """Best-effort LLM summary title; falls back to a truncated user message on failure.

    Reuses the caller's chat model (not a hardcoded one) so the title call
    succeeds against whichever provider/API key the chat itself just used.
    """
    fallback = user_message.strip()[:60] or "New chat"
    try:
        prompt = f"User: {user_message}"
        if assistant_reply:
            prompt += f"\nAssistant: {assistant_reply[:1000]}"
        title = complete(prompt, model=model, system=_TITLE_SYSTEM_PROMPT, max_tokens=20)
        title = title.strip().strip('"').strip()
        return title[:200] if title else fallback
    except Exception:
        return fallback
