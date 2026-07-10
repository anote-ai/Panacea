"""Tests for the document Q&A MCP server engine (mcp_server.core).

Chroma and the LLM are mocked — tests cover extraction, chunk metadata,
registry behaviour, retrieval shaping, and error paths.
"""
from unittest.mock import MagicMock

import pytest

from mcp_server import core


@pytest.fixture
def data_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ANOTE_MCP_DATA_DIR", str(tmp_path))
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    return tmp_path


@pytest.fixture
def collection(monkeypatch):
    fake = MagicMock()
    fake.query.return_value = {"documents": [[]], "metadatas": [[]], "distances": [[]]}
    monkeypatch.setattr(core, "_collection", lambda: fake)
    return fake


def _upload_txt(tmp_path, content="Hello world. " * 200, project="proj"):
    doc = tmp_path / "sample.txt"
    doc.write_text(content)
    return core.upload_document(str(doc), project_name=project)


# ── upload_document ───────────────────────────────────────────────────────────


def test_upload_indexes_and_registers(data_dir, collection):
    result = _upload_txt(data_dir)
    assert result["status"] == "indexed"
    assert result["pages"] == 1

    kwargs = collection.add.call_args.kwargs
    assert len(kwargs["documents"]) > 1  # long text → multiple chunks
    meta = kwargs["metadatas"][0]
    assert meta["document_id"] == result["document_id"]
    assert meta["project"] == "proj"
    assert meta["page"] == 1

    listed = core.list_documents("proj")
    assert [d["id"] for d in listed] == [result["document_id"]]
    assert listed[0]["name"] == "sample.txt"
    assert listed[0]["pages"] == 1


def test_upload_missing_file_raises(data_dir, collection):
    with pytest.raises(ValueError, match="file not found"):
        core.upload_document(str(data_dir / "nope.txt"), project_name="proj")


def test_upload_unsupported_type_raises(data_dir, collection):
    bad = data_dir / "image.png"
    bad.write_bytes(b"\x89PNG")
    with pytest.raises(ValueError, match="unsupported file type"):
        core.upload_document(str(bad), project_name="proj")


def test_upload_requires_project(data_dir, collection):
    with pytest.raises(ValueError, match="project_name"):
        core.upload_document("whatever.txt", project_name="  ")


def test_upload_from_url(data_dir, collection, monkeypatch):
    response = MagicMock()
    response.content = b"Downloaded text content."
    response.headers = {"Content-Type": "text/plain; charset=utf-8"}
    monkeypatch.setattr("requests.get", lambda url, timeout: response)

    result = core.upload_document("https://example.com/notes", project_name="proj")
    assert result["status"] == "indexed"
    assert core.list_documents("proj")[0]["name"] == "notes"


def test_list_documents_scoped_to_project(data_dir, collection):
    _upload_txt(data_dir, project="a")
    assert core.list_documents("a") != []
    assert core.list_documents("b") == []


# ── ask_question ──────────────────────────────────────────────────────────────


def test_ask_question_requires_target(data_dir, collection):
    with pytest.raises(ValueError, match="document_id or project_id"):
        core.ask_question("what?")


def test_ask_question_no_results(data_dir, collection):
    result = core.ask_question("what?", project_id="proj")
    assert result["confidence"] == 0.0
    assert result["sources"] == []


def test_ask_question_shapes_sources_and_filters(data_dir, collection, monkeypatch):
    collection.query.return_value = {
        "documents": [["chunk one", "chunk two"]],
        "metadatas": [[{"page": 3}, {"page": 7}]],
        "distances": [[0.0, 1.0]],
    }
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setattr(core, "complete", lambda prompt, model: "the answer")

    result = core.ask_question("what?", document_id="doc-1", top_k=2)
    assert result["answer"] == "the answer"
    assert result["confidence"] == 1.0
    assert result["sources"] == [
        {"chunk": "chunk one", "page": 3, "score": 1.0},
        {"chunk": "chunk two", "page": 7, "score": 0.5},
    ]
    assert collection.query.call_args.kwargs["where"] == {"document_id": "doc-1"}


def test_ask_question_without_api_key_returns_context(data_dir, collection):
    collection.query.return_value = {
        "documents": [["relevant chunk"]],
        "metadatas": [[{"page": 1}]],
        "distances": [[0.2]],
    }
    result = core.ask_question("what?", project_id="proj")
    assert "relevant chunk" in result["answer"]
    assert result["confidence"] > 0


# ── summarize_document ────────────────────────────────────────────────────────


def test_summarize_unknown_document_raises(data_dir, collection):
    with pytest.raises(ValueError, match="unknown document"):
        core.summarize_document("missing")


def test_summarize_with_focus(data_dir, collection, monkeypatch):
    uploaded = _upload_txt(data_dir)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    prompts = []

    def fake_complete(prompt, model):
        prompts.append(prompt)
        return "a summary"

    monkeypatch.setattr(core, "complete", fake_complete)
    result = core.summarize_document(uploaded["document_id"], focus="key risks")
    assert result == {"summary": "a summary"}
    assert "Focus on: key risks." in prompts[0]


def test_summarize_without_api_key_returns_preview(data_dir, collection):
    uploaded = _upload_txt(data_dir, content="Preview me.")
    result = core.summarize_document(uploaded["document_id"])
    assert "Preview me." in result["summary"]
