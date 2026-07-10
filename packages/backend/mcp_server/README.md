# Anote Document Q&A — MCP Server

Point any MCP client (Claude Code, LangChain, custom agents) at your documents
and ask questions about them. Implements issue #206 with four tools:

| Tool | What it does |
|------|--------------|
| `upload_document(file_path, project_name)` | Index a local file or URL (pdf/txt/md/csv) into a project |
| `list_documents(project_id)` | List a project's indexed documents |
| `ask_question(question, document_id \| project_id, top_k=5)` | RAG answer with per-chunk sources, pages, and scores |
| `summarize_document(document_id, focus=None)` | Summarize a document, optionally focused ("key risks", …) |

## 5-minute quickstart

```bash
cd packages/backend
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...   # any provider supported by services/llm.py works

# Register with Claude Code:
claude mcp add anote-docs -- python -m mcp_server.server
```

Then, in a Claude Code session:

> Upload ~/contracts/msa.pdf to project "legal", then tell me what the
> termination clauses are.

Claude will call `upload_document`, then `ask_question` — answers come back
with page numbers and similarity scores per source.

### Or configure any MCP client manually

```json
{
  "mcpServers": {
    "anote-docs": {
      "command": "python",
      "args": ["-m", "mcp_server.server"],
      "cwd": "/path/to/packages/backend"
    }
  }
}
```

## Python API (no MCP required)

The engine is importable directly — this is the clean API that
`anote-mcp-server` wraps:

```python
from mcp_server import upload_document, ask_question, summarize_document

doc = upload_document("report.pdf", project_name="research")
print(ask_question("What are the key findings?", document_id=doc["document_id"]))
print(summarize_document(doc["document_id"], focus="executive summary"))
```

Run with `packages/backend` on `PYTHONPATH` (or as cwd).

## Configuration

| Env var | Default | Purpose |
|---------|---------|---------|
| `ANOTE_MCP_DATA_DIR` | `~/.anote` | Document registry + downloads + vector store |
| `CHROMA_PERSIST_DIR` | `$ANOTE_MCP_DATA_DIR/chroma_db` | Chroma vector store location |
| `ANOTE_MCP_MODEL` | `claude-sonnet-4-6` | Model used for answering/summarizing |
| `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` | — | LLM provider credentials |

Without an API key the server still works: `ask_question` returns the most
relevant retrieved context instead of a generated answer.

## Notes

- Storage is persistent (SQLite registry + persistent Chroma collection under
  the data dir), so indexed documents survive restarts.
- PDF pages are tracked through chunking, so sources cite real page numbers.
- Supersedes the legacy prototype in `/backend/mcp/` (root backend), which
  depends on the undeployed financeGPT stack.
- PyPI packaging (`autonomous-intelligence-mcp`) is a follow-up once the
  release pipeline (PR #257) lands.
