# Local Models

The bundled backend supports local LLM inference via [Ollama](https://ollama.ai) — any model name that isn't a `claude*`, `gpt*`, or `gemini*` model is routed to Ollama automatically (`packages/backend/services/llm.py`).

!!! warning "Desktop UI gap"
    The desktop app's chat model dropdown is currently a fixed list of 4 cloud models (`claude-sonnet-4-6`, `claude-haiku-4-5-20251001`, `gpt-4o`, `gpt-4o-mini`) with no local-model option wired in yet. The backend routing described below works today; picking a local model from the desktop app's UI doesn't. If you need this, it's worth raising as a small frontend addition rather than assuming it already works.

## Setup

1. Install Ollama from [ollama.ai](https://ollama.ai)
2. Pull a model:

   ```bash
   ollama pull llama3
   ollama pull mistral
   ```

3. The backend defaults to `OLLAMA_BASE_URL=http://localhost:11434`; override it in your `.env` if Ollama runs elsewhere
4. Send the exact model name (e.g. `llama3`, no prefix) as the `model` in any `chat` call — via CLI, SDK, or once the desktop UI supports it

## Supported Models

| Model | Pull Command |
|-------|--------------|
| Llama 3 | `ollama pull llama3` |
| Mistral | `ollama pull mistral` |
| Phi-3 | `ollama pull phi3` |

Local models run entirely on your hardware — no data leaves your machine.
