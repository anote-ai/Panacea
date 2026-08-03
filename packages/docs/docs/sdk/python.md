# Python SDK

`anote-sdk` is the Python client for the Anote REST API — a direct mirror of the [TypeScript SDK](typescript.md), with both a synchronous and an `asyncio` client. Package source: `packages/sdk-py/`.

!!! note "API keys and local development"
    Same caveat as the TypeScript SDK: the client talks to `https://api.anote.ai` by default and authenticates with an API key. This repo's local backend doesn't currently issue those keys — only JWT session auth for the web app. Use a key from your hosted Anote account, or confirm with the backend team before pointing this at a local server.

## What you'll need

- Python 3.9+
- An Anote API key from your account

## 1. Install

```bash
pip install anote-sdk
```

## 2. Initialize the client

```python
from anote_sdk import AnoteClient

client = AnoteClient(api_key="your-api-key")
# or: AnoteClient(api_key="...", base_url="https://api.anote.ai", timeout=60.0)
```

`api_key` is the only required argument.

## 3. Send your first message

```python
result = client.chat("Explain this codebase")

print(result.result)
print(f"Used {result.usage.input_tokens} input tokens")
```

Pass `cwd`, `model`, or `tools` to scope the call:

```python
client.chat(
    "List TODOs in this file",
    cwd="/path/to/project",
    model="claude-sonnet-4-6",
    tools=["Read", "Grep"],
)
```

## Common tasks

**List and inspect past sessions**

```python
sessions = client.list_sessions()
messages = client.get_session_messages(sessions[0].session_id)
```

**Search across session history**

```python
results = client.search("authentication logic")
```

**Check your usage and quota**

```python
usage = client.get_usage()
print(f"{usage.remaining.requests} requests remaining this month")
```

**Share a session as a read-only link**

```python
share = client.share_session(sessions[0].session_id)
print(share.share_url)
```

**Handle errors**

Every non-2xx response raises `AnoteError`, which carries `.status` and `.body`:

```python
from anote_sdk import AnoteClient, AnoteError

try:
    client.chat("...")
except AnoteError as err:
    print(err.status, err)  # e.g. 429, "Monthly quota exceeded"
```

**Check server liveness (no auth required)**

```python
health = client.health()
```

## Async usage

For `asyncio` applications, use `AsyncAnoteClient` as a context manager — same method names, `await`ed:

```python
from anote_sdk import AsyncAnoteClient

async with AsyncAnoteClient(api_key="your-api-key") as client:
    result = await client.chat("Explain this codebase")
    print(result.result)
```

## API reference

### `AnoteClient(api_key, base_url=..., timeout=60.0)` / `AsyncAnoteClient(...)`

| Argument | Type | Required | Description |
|---|---|---|---|
| `api_key` | `str` | ✓ | Your Anote API key |
| `base_url` | `str` | | Server URL (default: `https://api.anote.ai`) |
| `timeout` | `float` | | Request timeout in seconds (default: `60.0`) |

### Methods

| Method | Description |
|--------|-------------|
| `chat(message, *, cwd=, model=, tools=)` | Send a message, get a complete AI response |
| `list_sessions()` | List all chat sessions |
| `get_session_messages(session_id)` | Get message history for a session |
| `delete_session(session_id)` | Delete a session |
| `share_session(session_id)` | Mint a shareable read-only link |
| `search(query, limit=20)` | Full-text search across sessions |
| `get_usage()` | Current month usage + quota |
| `health()` | Server liveness check (no auth needed) |

Async client exposes the same methods as coroutines.

## Next steps

- [Backend API Overview](../api/overview.md) — the REST endpoints underneath this SDK
- [TypeScript SDK](typescript.md) — the equivalent JS/TS client
