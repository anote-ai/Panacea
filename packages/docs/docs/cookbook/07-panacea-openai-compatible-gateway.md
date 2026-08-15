# Panacea OpenAI-Compatible API Gateway

This recipe explains how to point any tool built against the OpenAI SDK at Panacea instead — with zero code changes — while still getting access to Panacea-specific RAG extensions like grounded document sources.

## What you'll learn

- How `AnoteOpenAI` mirrors the real `openai.OpenAI` client's interface
- How to upload documents and get document-grounded answers through a chat-completions-shaped API
- How streaming works over Server-Sent Events (SSE), OpenAI-style
- Where the Panacea-specific extensions (`anote_sources`, `anote_message_id`) show up in the response

## Why this matters

A huge amount of existing tooling — LangChain integrations, internal scripts, third-party agent frameworks — is written against the OpenAI SDK's shape (`client.chat.completions.create(...)`, `client.models.list()`). Rather than asking every integrator to learn a bespoke Panacea SDK, Panacea ships a drop-in client that speaks the same interface, so teams can adopt Panacea's private, document-grounded backend without rewriting their integration code.

## Key Panacea files

| File | Why it matters |
|---|---|
| `Panacea/backend/sdk/anoteai/openai_compat.py` | `AnoteOpenAI` client: `CompletionsClient`, `ModelsClient`, `DocumentsClient`, and the SSE stream parser |
| `Panacea/backend/sdk/anoteai/core.py` | The underlying `PrivateChatbot` SDK class that the compat layer wraps |
| `Panacea/backend/sdk/anoteai/handlers/private_handlers.py` | Request handling shared with the native SDK |
| Server routes: `POST /v1/chat/completions`, `GET /v1/models`, `POST /v1/question-answer`, `POST /public/upload` | The OpenAI-shaped (and one Panacea-specific) endpoints the client calls |

## How it works

1. Instantiate the client exactly like the OpenAI SDK, but pointed at your Panacea backend:

   ```python
   from anoteai.openai_compat import AnoteOpenAI

   client = AnoteOpenAI(
       api_key="your-anote-api-key",       # or set ANOTE_API_KEY
       base_url="http://localhost:5000",    # or https://api.anote.ai
   )
   ```

2. For document-grounded Q&A, upload files first — `client.documents.upload(...)` posts multipart form data to `/public/upload` and returns a `chat_id`.
3. Ask a question the same way you'd call the OpenAI SDK, passing the `chat_id` through `extra_body` so the server knows which documents to retrieve against:

   ```python
   upload_resp = client.documents.upload("path/to/report.pdf")
   chat_id = upload_resp["chat_id"]

   response = client.chat.completions.create(
       model="gpt-4o",
       messages=[{"role": "user", "content": "Summarise the key findings."}],
       extra_body={"chat_id": chat_id},
   )
   print(response.choices[0].message.content)
   print("Sources:", response.anote_sources)
   ```

4. The response is mapped into dataclasses that mirror the real OpenAI SDK (`ChatCompletion`, `Choice`, `Message`, `Usage`), plus two Panacea extensions: `anote_message_id` and `anote_sources` (the retrieved chunks/citations backing the answer).
5. Pass `stream=True` to get a generator of `ChatCompletionChunk` objects parsed from `text/event-stream` SSE lines (`data: {...}` per token, terminated by `data: [DONE]`) — the same shape OpenAI's streaming client produces.
6. `client.models.list()` calls `GET /v1/models` for model discovery, returning `Model`/`ModelList` objects just like the OpenAI SDK.

## Run it locally

From the workspace root (`anote/panacea`):

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

Install the client's one dependency and set your API key:

```bash
pip install requests
export ANOTE_API_KEY=your_api_key_here   # macOS/Linux
set ANOTE_API_KEY=your_api_key_here      # Windows cmd
```

### Minimal walkthrough

```python
from anoteai.openai_compat import AnoteOpenAI

client = AnoteOpenAI(base_url="http://localhost:5000")

# Plain chat, no documents:
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "What is the capital of France?"}],
)
print(response.choices[0].message.content)

# Streaming:
for chunk in client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Count to five."}],
    stream=True,
):
    for choice in chunk.choices:
        if choice.delta.content:
            print(choice.delta.content, end="", flush=True)
```

## Notes for the cookbook

This recipe is a good complement to recipe 03 — it's the same document Q&A/RAG capability, but exposed through an interface that existing OpenAI-SDK-based tooling can consume unmodified. Worth flagging to readers that `DocumentsClient.upload()`/`question_answer()` are Panacea-specific helpers layered on top of the OpenAI-compatible core, not part of the OpenAI spec itself.
