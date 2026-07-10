"""Tests for the answer-quality slice of #204 (services.rag).

Chroma and the LLM are mocked via the _query_collection / _expand_query
seams — tests cover variant merging, re-ranking, confidence, and the
endpoint response shape.
"""
import io

from services import rag


def _results(chunks, distances, ids=None):
    return {
        "documents": [chunks],
        "distances": [distances],
        "ids": [ids or [f"c{i}" for i in range(len(chunks))]],
    }


# ── re-ranking ────────────────────────────────────────────────────────────────


def test_rerank_lexical_overlap_beats_closer_vector():
    candidates = [
        {"chunk": "Something entirely unrelated to the topic.", "distance": 0.1},
        {"chunk": "The termination clause requires 30 days notice.", "distance": 0.4},
    ]
    ranked = rag._rerank("What does the termination clause say?", candidates)
    assert ranked[0]["chunk"].startswith("The termination clause")
    assert ranked[0]["score"] > ranked[1]["score"]


def test_rerank_empty_candidates():
    assert rag._rerank("anything", []) == []


# ── retrieval merging ─────────────────────────────────────────────────────────


def test_retrieve_dedupes_across_variants_keeping_best_distance(monkeypatch):
    results = {
        "documents": [["shared chunk", "only-a"], ["shared chunk", "only-b"]],
        "distances": [[0.5, 0.3], [0.2, 0.6]],
        "ids": [["shared", "a"], ["shared", "b"]],
    }
    monkeypatch.setattr(rag, "_query_collection", lambda *args, **kwargs: results)
    candidates = rag._retrieve(["q1", "q2"], None, top_k=5)
    by_chunk = {c["chunk"]: c["distance"] for c in candidates}
    assert len(candidates) == 3
    assert by_chunk["shared chunk"] == 0.2  # best distance wins


def test_retrieve_tolerates_missing_ids_and_distances(monkeypatch):
    monkeypatch.setattr(
        rag, "_query_collection", lambda *args, **kwargs: {"documents": [["chunk1", "chunk2"]]}
    )
    candidates = rag._retrieve(["q"], None, top_k=5)
    assert len(candidates) == 2
    assert all(c["distance"] == 1.0 for c in candidates)


def test_retrieve_chroma_failure_returns_empty(monkeypatch):
    monkeypatch.setattr(rag, "_query_collection", lambda *args, **kwargs: None)
    assert rag._retrieve(["q"], None, top_k=5) == []


# ── answer_question ───────────────────────────────────────────────────────────


def test_answer_question_no_results(monkeypatch):
    monkeypatch.setattr(rag, "_query_collection", lambda *args, **kwargs: None)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    result = rag.answer_question("what?")
    assert result["confidence"] == 0.0
    assert result["low_confidence"] is True
    assert result["warning"] == rag.LOW_CONFIDENCE_WARNING
    assert result["sources"] == []


def test_answer_question_confident_no_key(monkeypatch):
    monkeypatch.setattr(
        rag,
        "_query_collection",
        lambda *args, **kwargs: _results(
            ["The vacation policy grants 20 days."], [0.1]
        ),
    )
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    result = rag.answer_question("How many vacation days in the policy?")
    assert "vacation policy" in result["answer"].lower()
    assert result["confidence"] > 0.45
    assert result["low_confidence"] is False
    assert result["warning"] is None
    assert result["sources"][0]["score"] == result["confidence"]


def test_answer_question_low_confidence_warns(monkeypatch):
    monkeypatch.setattr(
        rag,
        "_query_collection",
        lambda *args, **kwargs: _results(["nothing to do with it"], [4.0]),
    )
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    result = rag.answer_question("completely different subject?")
    assert result["low_confidence"] is True
    assert result["warning"] == rag.LOW_CONFIDENCE_WARNING


def test_answer_question_uses_expanded_variants(monkeypatch):
    seen = {}

    def fake_query(variants, doc_ids, n_results):
        seen["variants"] = variants
        return _results(["chunk"], [0.2])

    monkeypatch.setattr(rag, "_query_collection", fake_query)
    monkeypatch.setattr(rag, "_expand_query", lambda q, m: ["variant one", "variant two"])
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    rag.answer_question("original?")
    assert seen["variants"] == ["original?", "variant one", "variant two"]


def test_expand_query_skipped_without_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert rag._expand_query("question?", "claude-sonnet-4-6") == []


def test_query_documents_compat_returns_string(monkeypatch):
    monkeypatch.setattr(rag, "_query_collection", lambda *args, **kwargs: None)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert isinstance(rag.query_documents("what?"), str)


# ── endpoint shape ────────────────────────────────────────────────────────────


def test_ask_endpoint_returns_confidence_and_sources(client, monkeypatch):
    monkeypatch.setattr("api_endpoints.documents.handler.ingest_document", lambda **kwargs: 1)
    monkeypatch.setattr(
        "api_endpoints.documents.handler.answer_question",
        lambda **kwargs: {
            "answer": "an answer",
            "confidence": 0.82,
            "sources": [{"chunk": "c", "score": 0.82}],
            "low_confidence": False,
            "warning": None,
        },
    )
    data = {"file": (io.BytesIO(b"Content."), "doc.txt")}
    doc_id = client.post(
        "/api/documents/upload", data=data, content_type="multipart/form-data"
    ).get_json()["id"]

    resp = client.post(f"/api/documents/{doc_id}/ask", json={"question": "?"})
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["confidence"] == 0.82
    assert body["sources"][0]["chunk"] == "c"
    assert body["lowConfidence"] is False
    assert body["warning"] is None
