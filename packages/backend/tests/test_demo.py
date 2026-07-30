"""Tests for the public no-auth demo endpoints (issue #200)."""
from __future__ import annotations

from unittest.mock import patch

import pytest

import api_endpoints.demo.handler as demo_handler
import services.demo as demo_service


@pytest.fixture(autouse=True)
def _reset_demo_state():
    demo_handler._question_counts.clear()
    demo_service._answer_cache.clear()
    yield
    demo_handler._question_counts.clear()
    demo_service._answer_cache.clear()


_FAKE_ANSWER = {
    "answer": "The company has $312 million in cash.",
    "sources": [
        {
            "chunk": "We ended the year with $312 million in cash and equivalents.",
            "docId": "demo-annual-report",
            "docName": "Meridian Robotics 2025 Annual Report",
            "score": 0.91,
        }
    ],
}


# ---------------------------------------------------------------------------
# GET /api/demo/documents
# ---------------------------------------------------------------------------

def test_list_demo_documents_no_auth(client):
    resp = client.get("/api/demo/documents")
    assert resp.status_code == 200
    body = resp.get_json()
    assert len(body["documents"]) == 3
    assert body["questionLimit"] == 5
    assert body["remaining"] == 5
    for doc in body["documents"]:
        assert doc["id"] and doc["name"] and doc["category"]
        assert len(doc["suggestedQuestions"]) == 3


def test_demo_sample_files_exist():
    for doc in demo_service.DEMO_DOCS:
        path = demo_service.DEMO_DIR / doc["file"]
        assert path.is_file(), f"missing demo file: {path}"
        assert len(path.read_text(encoding="utf-8")) > 500


# ---------------------------------------------------------------------------
# POST /api/demo/ask
# ---------------------------------------------------------------------------

def test_ask_demo_no_auth_returns_answer_and_sources(client):
    with patch("api_endpoints.demo.handler.ensure_indexed"), \
         patch("api_endpoints.demo.handler.answer_demo_question", return_value=_FAKE_ANSWER):
        resp = client.post("/api/demo/ask", json={"question": "How much cash?"})
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["answer"] == _FAKE_ANSWER["answer"]
    assert body["sources"][0]["docName"] == "Meridian Robotics 2025 Annual Report"
    assert body["remaining"] == 4


def test_ask_demo_requires_question(client):
    resp = client.post("/api/demo/ask", json={})
    assert resp.status_code == 400


def test_ask_demo_rejects_overlong_question(client):
    resp = client.post("/api/demo/ask", json={"question": "x" * 501})
    assert resp.status_code == 400


def test_ask_demo_unknown_document(client):
    resp = client.post("/api/demo/ask", json={"question": "hi", "docId": "not-a-demo-doc"})
    assert resp.status_code == 404


def test_ask_demo_enforces_five_question_limit(client):
    with patch("api_endpoints.demo.handler.ensure_indexed"), \
         patch("api_endpoints.demo.handler.answer_demo_question", return_value=_FAKE_ANSWER):
        for expected_remaining in (4, 3, 2, 1, 0):
            resp = client.post("/api/demo/ask", json={"question": "q?"})
            assert resp.status_code == 200
            assert resp.get_json()["remaining"] == expected_remaining
        resp = client.post("/api/demo/ask", json={"question": "one more?"})
    assert resp.status_code == 429
    body = resp.get_json()
    assert body["signupRequired"] is True
    assert body["remaining"] == 0


def test_ask_demo_limit_reflected_in_document_listing(client):
    with patch("api_endpoints.demo.handler.ensure_indexed"), \
         patch("api_endpoints.demo.handler.answer_demo_question", return_value=_FAKE_ANSWER):
        client.post("/api/demo/ask", json={"question": "q?"})
        client.post("/api/demo/ask", json={"question": "r?"})
    resp = client.get("/api/demo/documents")
    assert resp.get_json()["remaining"] == 3


# ---------------------------------------------------------------------------
# services.demo caching
# ---------------------------------------------------------------------------

def test_answer_demo_question_caches_identical_questions():
    sources = [{"chunk": "text", "docId": "demo-llm-paper", "docName": "Paper", "score": 0.8}]
    with patch("services.demo.ensure_indexed"), \
         patch("services.demo.retrieve_demo_chunks", return_value=sources), \
         patch("services.demo._generate_answer", return_value="cached answer") as mock_gen:
        first = demo_service.answer_demo_question("What Chunk size  worked best?")
        second = demo_service.answer_demo_question("what chunk size worked best?")
    assert first == second
    assert mock_gen.call_count == 1


def test_answer_demo_question_no_sources():
    with patch("services.demo.ensure_indexed"), \
         patch("services.demo.retrieve_demo_chunks", return_value=[]):
        result = demo_service.answer_demo_question("unanswerable?")
    assert result["sources"] == []
    assert "could not find" in result["answer"]
