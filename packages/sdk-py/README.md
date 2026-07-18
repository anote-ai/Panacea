# anote-sdk

Python SDK for the Anote AI assistant REST API.

## Installation

```bash
pip install anote-sdk
```

## Usage

```python
from anote_sdk import AnoteClient

client = AnoteClient(api_key="<jwt-access-token>", base_url="http://localhost:5000")

result = client.chat("Explain this codebase")
print(result.response)

for chunk in client.chat_stream("Explain this codebase"):
    print(chunk, end="", flush=True)

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

## Development

```bash
pip install -e ".[dev]"
pytest
```
