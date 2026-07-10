"""RAG pipeline — document ingestion and retrieval.

Answer quality (#204, backend slice): retrieval expands the user's question
into alternative phrasings (LLM, best-effort), merges + dedupes candidates
across variants, re-ranks them with a lightweight blend of vector similarity
and lexical overlap, and reports a confidence score with per-chunk sources.
A cross-encoder re-ranker and the chunk-size benchmark are follow-ups.
"""
from __future__ import annotations

import re
from pathlib import Path

# Hardcoded upload directory — not derived from env so CodeQL taint stops here
_UPLOAD_DIR: Path = Path("/tmp/anote_uploads").resolve()
_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Public alias used by other modules
UPLOAD_FOLDER = _UPLOAD_DIR

# Blend weights for re-ranking and the low-confidence threshold
_VECTOR_WEIGHT = 0.7
_LEXICAL_WEIGHT = 0.3
_LOW_CONFIDENCE_THRESHOLD = 0.45

LOW_CONFIDENCE_WARNING = (
    "I found limited relevant information. Consider rephrasing your question."
)

# Function words excluded from the lexical-overlap signal
_STOPWORDS = {
    "the", "and", "for", "are", "was", "were", "not", "but", "all", "any",
    "what", "when", "where", "which", "who", "why", "how", "does", "did",
    "this", "that", "these", "those", "with", "from", "into", "about",
    "have", "has", "had", "can", "could", "would", "should", "will", "you",
}

_NOT_FOUND_ANSWER = "I could not find relevant information in the documents."


def ingest_document(doc_id: str, file_path: Path) -> int:
    """Ingest a document into the vector store. Returns chunk count."""
    # Prevent path traversal: file_path must be within the upload directory
    resolved = file_path.resolve()
    if not str(resolved).startswith(str(_UPLOAD_DIR) + "/"):
        raise ValueError("Access to file outside upload folder is not allowed")
    text = _extract_text(resolved)
    chunks = _chunk_text(text)
    if not chunks:
        return 0
    try:
        import os

        import chromadb
        from chromadb.utils import embedding_functions
        client = chromadb.PersistentClient(path=os.environ.get("CHROMA_PERSIST_DIR", "./chroma_db"))
        ef = embedding_functions.DefaultEmbeddingFunction()
        collection = client.get_or_create_collection(
            "documents", embedding_function=ef  # type: ignore[arg-type]
        )
        ids = [f"{doc_id}-{i}" for i in range(len(chunks))]
        collection.add(documents=chunks, ids=ids, metadatas=[{"doc_id": doc_id}] * len(chunks))
    except Exception:
        pass
    return len(chunks)


def answer_question(
    question: str,
    doc_ids: list[str] | None = None,
    model: str = "claude-sonnet-4-6",
    top_k: int = 5,
) -> dict:
    """Answer a question using RAG, with confidence and per-chunk sources.

    Returns {"answer", "confidence", "sources": [{"chunk", "score"}],
    "low_confidence", "warning"}.
    """
    variants = [question, *_expand_query(question, model)]
    candidates = _retrieve(variants, doc_ids, top_k)
    ranked = _rerank(question, candidates)[:top_k]

    if not ranked:
        return {
            "answer": _NOT_FOUND_ANSWER,
            "confidence": 0.0,
            "sources": [],
            "low_confidence": True,
            "warning": LOW_CONFIDENCE_WARNING,
        }

    confidence = ranked[0]["score"]
    low_confidence = confidence < _LOW_CONFIDENCE_THRESHOLD
    context = "\n\n".join(source["chunk"] for source in ranked)

    import os
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        answer = f"Context found: {context[:500]}"
    else:
        import anthropic
        client_llm = anthropic.Anthropic(api_key=api_key)
        prompt = f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer:"
        response = client_llm.messages.create(
            model=model,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],  # type: ignore[list-item]
        )
        block = response.content[0] if response.content else None
        answer = block.text if block and hasattr(block, "text") else ""  # type: ignore[union-attr]

    return {
        "answer": answer,
        "confidence": confidence,
        "sources": ranked,
        "low_confidence": low_confidence,
        "warning": LOW_CONFIDENCE_WARNING if low_confidence else None,
    }


def query_documents(
    question: str,
    doc_ids: list[str] | None = None,
    model: str = "claude-sonnet-4-6",
    top_k: int = 5,
) -> str:
    """Answer a question using RAG (compat wrapper around answer_question)."""
    return answer_question(question, doc_ids=doc_ids, model=model, top_k=top_k)["answer"]


def _expand_query(question: str, model: str) -> list[str]:
    """Generate alternative phrasings of the question via the LLM (best-effort).

    Catches wording mismatches between the user's question and the document's
    terminology. Skipped without an API key; never raises.
    """
    import os
    if not os.environ.get("ANTHROPIC_API_KEY", ""):
        return []
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        response = client.messages.create(
            model=model,
            max_tokens=200,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Rewrite this question two different ways using different "
                        "wording. Reply with only the two rewrites, one per line.\n\n"
                        f"Question: {question}"
                    ),
                }  # type: ignore[list-item]
            ],
        )
        block = response.content[0] if response.content else None
        text = block.text if block and hasattr(block, "text") else ""  # type: ignore[union-attr]
        return [line.strip() for line in text.splitlines() if line.strip()][:2]
    except Exception:
        return []


def _query_collection(
    variants: list[str], doc_ids: list[str] | None, n_results: int
) -> dict | None:
    """Run the Chroma query; returns the raw result dict or None on failure."""
    import os
    try:
        import chromadb
        from chromadb.utils import embedding_functions
        client = chromadb.PersistentClient(path=os.environ.get("CHROMA_PERSIST_DIR", "./chroma_db"))
        ef = embedding_functions.DefaultEmbeddingFunction()
        collection = client.get_or_create_collection(
            "documents", embedding_function=ef  # type: ignore[arg-type]
        )
        where: dict | None = {"doc_id": {"$in": doc_ids}} if doc_ids else None  # type: ignore[type-arg]
        return collection.query(  # type: ignore[return-value]
            query_texts=variants, n_results=n_results, where=where
        )
    except Exception:
        return None


def _retrieve(variants: list[str], doc_ids: list[str] | None, top_k: int) -> list[dict]:
    """Retrieve candidate chunks for all query variants, deduped by chunk id.

    A chunk found by several variants keeps its best (smallest) distance.
    Tolerates result dicts missing ids/distances (defaults are neutral).
    """
    results = _query_collection(variants, doc_ids, n_results=max(1, top_k) * 2)
    if not results:
        return []

    docs_lists = results.get("documents") or []
    ids_lists = results.get("ids") or []
    dist_lists = results.get("distances") or []

    best: dict[str, dict] = {}
    for qi, docs in enumerate(docs_lists):
        ids = ids_lists[qi] if qi < len(ids_lists) else []
        distances = dist_lists[qi] if qi < len(dist_lists) else []
        for i, chunk in enumerate(docs or []):
            chunk_id = ids[i] if i < len(ids) else f"variant{qi}-chunk{i}"
            distance = float(distances[i]) if i < len(distances) else 1.0
            existing = best.get(chunk_id)
            if existing is None or distance < existing["distance"]:
                best[chunk_id] = {"chunk": chunk, "distance": distance}
    return list(best.values())


def _rerank(question: str, candidates: list[dict]) -> list[dict]:
    """Score candidates by blended vector similarity + lexical overlap.

    Lightweight stand-in for a cross-encoder: keyword overlap demotes chunks
    that are semantically close but don't mention the question's terms.
    Returns [{"chunk", "score"}] sorted best-first.
    """
    keywords = {
        w for w in re.findall(r"[a-z0-9]+", question.lower())
        if len(w) > 2 and w not in _STOPWORDS
    }
    ranked = []
    for candidate in candidates:
        vector_score = 1.0 / (1.0 + max(0.0, candidate["distance"]))
        chunk_lower = candidate["chunk"].lower()
        lexical_score = (
            sum(1 for w in keywords if w in chunk_lower) / len(keywords) if keywords else 0.0
        )
        score = round(_VECTOR_WEIGHT * vector_score + _LEXICAL_WEIGHT * lexical_score, 4)
        ranked.append({"chunk": candidate["chunk"], "score": score})
    ranked.sort(key=lambda item: item["score"], reverse=True)
    return ranked


def _extract_text(file_path: Path) -> str:
    # Validate again at extraction time — defensive in-depth
    if not str(file_path.resolve()).startswith(str(_UPLOAD_DIR) + "/"):
        return ""
    ext = file_path.suffix.lower()
    if ext in (".txt", ".md", ".csv"):
        return file_path.read_text(encoding="utf-8", errors="ignore")
    if ext == ".pdf":
        try:
            import PyPDF2
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                return "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception:
            return ""
    return ""


def _chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> list[str]:
    if not text.strip():
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks
