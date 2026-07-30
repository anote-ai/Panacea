# Panacea Multi-Modal Document Ingestion

This recipe explains how Panacea extends document Q&A + RAG (see [recipe 03](../03-panacea-document-qa-rag/)) beyond plain text to images, audio, video, and spreadsheets — making all of them searchable through the same chunking and embedding pipeline.

## What you'll learn

- How Panacea classifies an upload by MIME type and routes it to a dedicated ingestion service
- How images and video frames are turned into indexable text using a vision-capable LLM
- How audio (including the audio track of a video) is transcribed with Whisper
- How spreadsheets are converted into Markdown tables instead of being flattened into an unsearchable text dump
- The feature flags and size limits that govern multi-modal ingestion

## Why this matters

Tika (the default document-text extractor) can only usefully handle text-based formats. Without extra handling, an uploaded image, audio clip, video, or spreadsheet would either fail to ingest or lose all of its structure. Panacea instead detects the media type at upload time and calls a purpose-built service that produces clean text, which is then stored as `document_text` and flows through the exact same retrieval path as any other document — so a screenshot, a call recording, or a sales spreadsheet all become answerable through chat like a PDF would.

## Key Panacea files

| File | Why it matters |
|---|---|
| `Panacea/backend/api_endpoints/documents/handler.py` | Detects MIME type/extension on upload and routes to the right ingestion service |
| `Panacea/backend/services/vision_service.py` | `describe_image()` — produces a detailed text description of an image using GPT-4o or Claude vision |
| `Panacea/backend/services/audio_service.py` | `transcribe_audio()` — transcribes audio with OpenAI Whisper |
| `Panacea/backend/services/video_service.py` | Extracts frames with `ffmpeg`, describes each with the vision service, transcribes the audio track, and interleaves both |
| `Panacea/backend/services/tabular_service.py` | `ingest_tabular()` — converts CSV/TSV/XLSX/XLS/ODS into Markdown tables that preserve headers and rows |
| `Panacea/backend/agents/config.py` | `AgentConfig` feature flags: `ENABLE_MULTIMODAL`, `MAX_IMAGE_BYTES`, `MAX_AUDIO_BYTES`, `MAX_VIDEO_BYTES`, `VIDEO_FRAME_INTERVAL_SECS`, `VIDEO_MAX_FRAMES` |

## How it works

1. A file is uploaded through the same endpoint used for regular documents; `handler.py` sniffs the MIME type/extension to classify it as image, video, audio, tabular, or plain text/document.
2. **Image** → `vision_service.describe_image()` sends the image (base64-encoded) to a vision-capable model with a prompt instructing it to transcribe any visible text, describe charts/diagrams/UI screenshots, and note objects and layout — so the description alone is enough for semantic search to find it later.
3. **Audio** → `audio_service.transcribe_audio()` calls Whisper (`whisper-1`) and returns a transcript with duration/language metadata.
4. **Video** → `video_service` extracts frames at a fixed interval (`VIDEO_FRAME_INTERVAL_SECS`, default 30s, capped at `VIDEO_MAX_FRAMES`) using `ffmpeg`, describes each frame with the vision service, transcribes the audio track separately, and interleaves both into one timestamped document.
5. **Tabular** → `tabular_service.ingest_tabular()` parses each sheet natively (via `csv`/`pandas`+`openpyxl`/`xlrd`) and renders it as a Markdown table, falling back to plain CSV for rows beyond the first 500 so nothing is lost from the search index even if it isn't rendered nicely.
6. Whatever text comes out of any of these services is stored as `document_text` and chunked/embedded exactly like a normal document, so it is retrievable through the standard RAG Q&A flow from recipe 03.

Every service is designed to **never raise** — a failed vision call, a missing dependency, or an oversized file returns a placeholder string (e.g. `"[Image too large for inline analysis (23.4 MB). Limit: 20 MB.]"`) so the document record is always created instead of failing the whole upload.

## Run it locally

From the workspace root (`anote/panacea`):

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

Multi-modal ingestion is on by default (`ENABLE_MULTIMODAL=true`). Set these in `backend/.env` to adjust behavior:

```bash
ENABLE_MULTIMODAL=true        # master switch
MAX_IMAGE_BYTES=20971520      # 20 MB default
MAX_AUDIO_BYTES=26214400      # 25 MB default
MAX_VIDEO_BYTES=524288000     # 500 MB default
VIDEO_FRAME_INTERVAL_SECS=30
VIDEO_MAX_FRAMES=20
```

Video ingestion additionally requires `ffmpeg` to be present on the backend container's `PATH` (already included in the provided Docker image). Excel ingestion requires `openpyxl` (XLSX/ODS) and `xlrd` (legacy XLS), and both vision/audio services need `OPENAI_API_KEY` and/or `ANTHROPIC_API_KEY` set depending on `DEFAULT_AGENT_MODEL_TYPE`.

### Try it

```bash
curl -X POST http://localhost:5000/ingest-pdf \
  -F chat_id=1 \
  -F "files[]=@./screenshot.png"

curl -X POST http://localhost:5000/ingest-pdf \
  -F chat_id=1 \
  -F "files[]=@./quarterly_sales.xlsx"
```

Then, in the web UI at `http://localhost:3000`, open the same chat session and ask a question about the image or spreadsheet you just uploaded — Panacea answers from the generated description/Markdown table exactly as it would from a PDF.

## Notes for the cookbook

This recipe pairs well with recipe 03: it's the same RAG pipeline, just with a wider funnel of input formats. Worth calling out to readers that the "index quality" for images/video is only as good as the vision model's description, so prompt tuning in `vision_service.py`'s `_INDEXING_PROMPT` is a natural customization point.
