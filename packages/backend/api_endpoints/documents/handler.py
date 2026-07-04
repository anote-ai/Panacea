"""Document endpoints — upload, list, delete, Q&A via RAG."""
from __future__ import annotations

import uuid
from pathlib import Path

from flask import Blueprint, current_app, jsonify, request

from services.document_store import DocumentStore
from services.rag import ingest_document, query_documents

documents_bp = Blueprint("documents", __name__, url_prefix="/api/documents")

# Map MIME types to safe extensions — extension never derived from user input
_MIME_TO_EXT: dict[str, str] = {
    "application/pdf": ".pdf",
    "text/plain": ".txt",
    "text/markdown": ".md",
    "text/csv": ".csv",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
}


def _store() -> DocumentStore:
    return DocumentStore(current_app.config["DOCUMENT_METADATA_DB_PATH"])


def _upload_folder() -> Path:
    folder = Path(current_app.config["UPLOAD_FOLDER"])
    folder.mkdir(parents=True, exist_ok=True)
    return folder


@documents_bp.post("/upload")
def upload() -> tuple:  # type: ignore[type-arg]
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    file = request.files["file"]

    # Derive extension only from MIME type so no user-controlled data flows to the path
    content_type = (file.content_type or "").split(";")[0].strip().lower()
    ext = _MIME_TO_EXT.get(content_type)
    if not ext:
        return jsonify({"error": "Unsupported file type"}), 400

    doc_id = str(uuid.uuid4())
    # save_path uses only server-generated UUID + server-validated ext
    save_path = _upload_folder() / f"{doc_id}{ext}"

    try:
        file.save(save_path)
    except Exception as exc:
        print(f"Save failed: {exc}")
        return jsonify({"error": "Internal server error"}), 500

    try:
        chunk_count = ingest_document(doc_id=doc_id, file_path=save_path)
    except Exception as exc:
        save_path.unlink(missing_ok=True)
        print(f"Ingestion failed: {exc}")
        return jsonify({"error": "Internal server error"}), 500

    original_name = file.filename or f"upload{ext}"
    document = _store().save_document(
        doc_id=doc_id,
        filename=original_name,
        path=save_path,
        chunks=chunk_count,
        content_type=content_type,
    )
    return jsonify(document), 201


@documents_bp.get("")
def list_documents() -> tuple:  # type: ignore[type-arg]
    return jsonify({"documents": _store().list_documents()}), 200


@documents_bp.get("/<doc_id>")
def get_document(doc_id: str) -> tuple:  # type: ignore[type-arg]
    doc = _store().get_document(doc_id)
    if not doc:
        return jsonify({"error": "Document not found"}), 404
    return jsonify(doc), 200


@documents_bp.delete("/<doc_id>")
def delete_document(doc_id: str) -> tuple:  # type: ignore[type-arg]
    doc = _store().delete_document(doc_id)
    if not doc:
        return jsonify({"error": "Document not found"}), 404
    Path(doc["path"]).unlink(missing_ok=True)
    return jsonify({"deleted": True}), 200


@documents_bp.post("/<doc_id>/ask")
def ask_document(doc_id: str) -> tuple:  # type: ignore[type-arg]
    if not _store().get_document(doc_id):
        return jsonify({"error": "Document not found"}), 404
    data = request.get_json(silent=True) or {}
    question = data.get("question", "").strip()
    if not question:
        return jsonify({"error": "question is required"}), 400
    model = data.get("model", "claude-sonnet-4-6")
    try:
        answer = query_documents(question=question, doc_ids=[doc_id], model=model)
        return jsonify({"answer": answer, "docId": doc_id}), 200
    except Exception as exc:
        print(f"Error answering document question: {exc}")
        return jsonify({"error": "Internal server error"}), 500
