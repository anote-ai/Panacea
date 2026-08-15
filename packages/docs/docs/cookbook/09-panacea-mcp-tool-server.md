# Panacea MCP Tool Server

This recipe explains how Panacea exposes its document/chat primitives as standard [Model Context Protocol](https://modelcontextprotocol.io/) (MCP) tools, so any MCP-compatible client (Claude Desktop, other MCP hosts) can use Panacea's retrieval and chat-history capabilities directly.

## What you'll learn

- The difference between this MCP surface and the internal agent/tool-registration architecture from recipe 04
- Which document and chat operations are exposed as MCP tools
- How document ingestion stays non-blocking via a Ray remote task
- Why the raw SQL passthrough tool is a security consideration worth calling out

## Why this matters

Recipe 04 covers how Panacea's *internal* orchestrator registers tools for its own agents to call. This is a different integration surface: it packages the same underlying document/chat functions as **external, standardized MCP tools** that any MCP client can invoke — no Panacea-specific SDK or API contract required, just the MCP protocol.

## Key Panacea files

| File | Why it matters |
|---|---|
| `Panacea/backend/mcp/mcp_server.py` | `FastMCP("Document Agent Server")` — defines all nine MCP tools |
| `Panacea/backend/api_endpoints/financeGPT/chatbot_endpoints.py` | The underlying DB-facing functions each MCP tool wraps (`get_relevant_chunks`, `add_document_to_db`, `chunk_document`, etc.) |
| `Panacea/backend/database/db.py` | `get_db_connection` — used directly by the `execute_database_query` tool |

## How it works

1. `mcp_server.py` initializes Ray (`ray.init(...)`) and a `FastMCP` server instance named `"Document Agent Server"`.
2. Each function decorated with `@mcp.tool()` wraps an existing Panacea function and returns a plain-text result or error string — the shape an LLM tool call expects back:
   - `retrieve_relevant_chunks(query, chat_id, user_email, k=2)` — semantic search over a chat's documents via `get_relevant_chunks`
   - `ingest_document(text, document_name, chat_id, chunk_size=1000)` — registers a document via `add_document_to_db`
   - `list_documents(chat_id, user_email)` / `delete_document(doc_id, user_email)` — document management
   - `add_message` / `get_chat_history` — chat history read/write
   - `add_sources_to_message` — attach citations to a stored message
   - `extract_text_from_url(url)` — fetch and return text content from a URL
   - `execute_database_query(query, params)` — raw SQL passthrough (see security note below)
3. `ingest_document` doesn't block on chunking — it calls `chunk_document.remote(text, chunk_size, doc_id)`, a Ray remote task, so large documents are processed asynchronously while the tool call returns immediately.
4. Running `python backend/mcp/mcp_server.py` starts `mcp.run()`, which serves these tools over MCP's stdio transport — ready for an MCP client to launch and connect to.
5. An MCP client (e.g. Claude Desktop) configured to launch this script gets access to all nine tools automatically, without writing any Panacea-specific integration code.

### Security note

`execute_database_query` executes an arbitrary SQL string against the production connection with no allow-list or read-only restriction — `SELECT` queries return rows as JSON, anything else commits and returns the affected-row count. Treat this as least-privilege territory: if you expose this server to an MCP client you don't fully trust, either remove this tool or scope its DB user to read-only access on non-sensitive tables.

## Run it locally

From the workspace root (`anote/panacea`):

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build   # brings up MySQL, Redis, Tika, and the backend
```

The MCP server needs `fastmcp` (not currently pinned in `backend/requirements.txt` — install it separately) and `ray>=2.9.0` (already in `backend/requirements.txt`):

```bash
pip install fastmcp
cd Panacea/backend
python mcp/mcp_server.py
```

### Connect an MCP client

Point an MCP-compatible client at the script, e.g. in Claude Desktop's `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "panacea-documents": {
      "command": "python",
      "args": ["/absolute/path/to/Panacea/backend/mcp/mcp_server.py"]
    }
  }
}
```

Restart the client, and the nine tools above become available to invoke from chat.

## Notes for the cookbook

Good follow-up to recipe 04 — contrast internal tool registration (`register_tool()` inside the orchestrator) with this external MCP surface. Also worth noting as a gap for readers: `fastmcp` isn't yet listed in `backend/requirements.txt`, so it needs a manual install until that's fixed upstream.
