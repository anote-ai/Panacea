"""Public demo — pre-loaded sample documents, no auth required (issue #200)."""
from __future__ import annotations

import os
from pathlib import Path

from services.rag import _chunk_text

DEMO_DIR = Path(__file__).resolve().parent.parent / "demo_data"
_COLLECTION = "demo_documents"

DEMO_DOCS: list[dict] = [
    {
        "id": "demo-annual-report",
        "name": "Meridian Robotics 2025 Annual Report",
        "category": "Financial",
        "file": "annual_report.md",
        "suggestedQuestions": [
            "What are the main risk factors?",
            "How much cash does the company have?",
            "How fast is the software segment growing?",
        ],
    },
    {
        "id": "demo-llm-paper",
        "name": "Research Paper: Retrieval Quality in Document Q&A",
        "category": "Academic",
        "file": "llm_research_paper.md",
        "suggestedQuestions": [
            "What matters more, retrieval or model scale?",
            "What chunk size worked best?",
            "What were the main failure modes?",
        ],
    },
    {
        "id": "demo-employment-contract",
        "name": "Sample Employment Agreement",
        "category": "Legal",
        "file": "employment_contract.md",
        "suggestedQuestions": [
            "How much notice do I have to give to resign?",
            "What severance is offered?",
            "Is there a non-compete clause?",
        ],
    },
]

_indexed = False
_answer_cache: dict[tuple[str, str], dict] = {}


def _get_collection():
    import chromadb
    from chromadb.utils import embedding_functions

    client = chromadb.PersistentClient(path=os.environ.get("CHROMA_PERSIST_DIR", "./chroma_db"))
    ef = embedding_functions.DefaultEmbeddingFunction()
    return client.get_or_create_collection(
        _COLLECTION, embedding_function=ef  # type: ignore[arg-type]
    )


def ensure_indexed() -> None:
    """Index the bundled sample documents once per process (idempotent)."""
    global _indexed
    if _indexed:
        return
    try:
        collection = _get_collection()
        for doc in DEMO_DOCS:
            existing = collection.get(where={"doc_id": doc["id"]}, limit=1)
            if existing.get("ids"):
                continue
            text = (DEMO_DIR / doc["file"]).read_text(encoding="utf-8")
            chunks = _chunk_text(text)
            collection.add(
                documents=chunks,
                ids=[f"{doc['id']}-{i}" for i in range(len(chunks))],
                metadatas=[{"doc_id": doc["id"], "doc_name": doc["name"]}] * len(chunks),
            )
        _indexed = True
    except Exception:
        pass


def retrieve_demo_chunks(question: str, doc_id: str | None = None, top_k: int = 4) -> list[dict]:
    """Return the most relevant sample-document chunks with citation metadata."""
    try:
        collection = _get_collection()
        where = {"doc_id": doc_id} if doc_id else None
        results = collection.query(
            query_texts=[question],
            n_results=top_k,
            where=where,  # type: ignore[arg-type]
            include=["documents", "metadatas", "distances"],  # type: ignore[list-item]
        )
        docs = (results.get("documents") or [[]])[0]
        metas = (results.get("metadatas") or [[]])[0]
        dists = (results.get("distances") or [[]])[0]
        sources = []
        for chunk, meta, dist in zip(docs, metas, dists):
            sources.append({
                "chunk": chunk,
                "docId": meta.get("doc_id", ""),
                "docName": meta.get("doc_name", ""),
                "score": round(1.0 / (1.0 + max(0.0, float(dist))), 3),
            })
        return sources
    except Exception:
        return []


def _generate_answer(question: str, context: str) -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return f"Context found: {context[:500]}"
    import anthropic

    client_llm = anthropic.Anthropic(api_key=api_key)
    prompt = (
        "Answer the question using only the context below from sample documents. "
        "Be concise and specific; if the context does not contain the answer, say so.\n\n"
        f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer:"
    )
    response = client_llm.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],  # type: ignore[list-item]
    )
    block = response.content[0] if response.content else None
    return block.text if block and hasattr(block, "text") else ""  # type: ignore[union-attr]


def answer_demo_question(question: str, doc_id: str | None = None) -> dict:
    """Answer a question against the sample documents, with sources. Cached per (doc, question)."""
    cache_key = (doc_id or "all", " ".join(question.lower().split()))
    cached = _answer_cache.get(cache_key)
    if cached is not None:
        return cached

    ensure_indexed()
    sources = retrieve_demo_chunks(question, doc_id)
    result: dict
    if not sources:
        result = {
            "answer": "I could not find relevant information in the sample documents.",
            "sources": [],
        }
    else:
        context = "\n\n".join(s["chunk"] for s in sources)
        result = {"answer": _generate_answer(question, context), "sources": sources}
    _answer_cache[cache_key] = result
    return result
