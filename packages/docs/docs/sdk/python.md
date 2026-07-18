# Python SDK

The `anote-sdk` package (`packages/sdk-py`) provides a typed client for the
Anote backend REST API — the same API described in [API Reference](../api/overview.md).

## Installation

```bash
pip install anote-sdk
```

## Usage

```python
from anote_sdk import AnoteClient

client = AnoteClient(api_key="<jwt-access-token>", base_url="http://localhost:5000")

# Non-streaming chat
result = client.chat("Explain this codebase")
print(result.response)

# Streaming chat
for chunk in client.chat_stream("Explain this codebase"):
    print(chunk, end="", flush=True)

# Codebase search (TF-IDF, requires `anote index` to have run first)
search = client.search("authentication logic")
for hit in search.results:
    print(hit.file, hit.start_line, hit.score)
```

An async client is also available:

```python
from anote_sdk import AsyncAnoteClient

async with AsyncAnoteClient(api_key="<jwt-access-token>") as client:
    result = await client.chat("Explain this codebase")
    print(result.response)
```

## API Reference

| Method | Description |
|--------|-------------|
| `chat(message, model=..., history=...)` | Send a message, get a complete response |
| `chat_stream(message, model=..., cwd=...)` | Send a message, yield response text chunks over SSE |
| `create_session()` | Create a new chat session, returns its ID |
| `list_sessions()` | List all chat session IDs |
| `get_session_messages(session_id)` | Get a session's message history |
| `delete_session(session_id)` | Delete a session |
| `search(query, cwd=..., top=...)` | TF-IDF search over the codebase index |
| `health()` | Health check (no auth required) |

See [`packages/sdk-py`](https://github.com/anote-ai/Panacea/tree/main/packages/sdk-py) for source and tests.
