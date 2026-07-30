# Panacea Document Q&A + RAG

This recipe explains how Panacea builds private document question-answering with retrieval-augmented generation (RAG).

## What you'll learn

- How Panacea ingests documents and stores them as searchable text
- How the backend retrieves relevant chunks for a question
- How the system uses embeddings and document sources to ground answers
- How Q&A feedback is captured and improves future responses

## Why this matters

Panacea is designed to let teams ask questions of private documents without sending them to a third-party chat service. The workflow is:

1. Upload documents
2. Chunk and embed content
3. Retrieve relevant chunks for a user query
4. Answer using an LLM with citations
5. Capture feedback to improve quality

## Key Panacea files

| File | Why it matters |
|---|---|
| `Panacea/backend/api_endpoints/documents/handler.py` | Document upload and ingestion API routes |
| `Panacea/backend/database/db.py` | Document storage and retrieval SQL logic |
| `Panacea/backend/database/qa_feedback.py` | Feedback capture for document Q&A |
| `Panacea/backend/agents/multi_agent_system.py` | Document retrieval agents used in multi-agent workflows |

## How it works

- Documents are uploaded through the backend and stored in `documents.document_text`.
- The system chunks large documents and creates retrieval metadata for fast lookup.
- When a user asks a question, Panacea selects one or more specialized agents to retrieve the best chunks and then generates an answer.
- The result includes source citations so users can trace the answer back to the original document.
- Feedback signals are logged in `qa_feedback` to enable future quality improvements.

## Run it locally

From the workspace root (`anote/panacea`):

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

This starts the backend, web app, MySQL, Redis, and Tika.

If you are already inside the recipe folder, use:

```bash
cd ../../../Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

Open `http://localhost:3000` to use the Panacea web UI. Document uploads are handled by the backend route `POST /ingest-pdf` with the required form fields `chat_id` and `files[]`.

Example upload command:

```bash
curl -X POST http://localhost:5000/ingest-pdf \
  -F chat_id=1 \
  -F "files[]=@./path/to/document.pdf"
```

### Minimal upload walkthrough

1. Start Panacea from the repo root:

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

2. In another terminal, upload a single text or PDF document:

```bash
curl -X POST http://localhost:5000/ingest-pdf \
  -F chat_id=1 \
  -F "files[]=@./Cookbook/recipes/03-panacea-document-qa-rag/data/sample-doc.txt"
```

3. Confirm the backend returns a successful `Document Uploaded` response.

4. Use the web UI at `http://localhost:3000` and select the same chat session to ask questions about the uploaded document.

If you want to test the API directly after upload, find the chat session ID in the UI or database and send questions through the app's chat flow. Panacea will retrieve relevant chunks and generate a grounded answer.

## Notes for the cookbook

This recipe is ideal for a cookbook entry that explains how Panacea supports private knowledge work. It is more conceptual than a one-line script, because the real value is understanding the document ingestion and retrieval architecture.
