"""Tests for document thumbnail generation."""
from __future__ import annotations

from services.thumbnails import generate_thumbnail, thumbnail_path


def test_thumbnail_path():
    from pathlib import Path

    assert thumbnail_path(Path("/uploads"), "abc") == Path("/uploads/abc_thumb.png")


def test_generate_thumbnail_pdf(tmp_path):
    import fitz

    pdf_path = tmp_path / "doc.pdf"
    doc = fitz.open()
    doc.new_page()
    doc.save(pdf_path)
    doc.close()

    ok = generate_thumbnail("doc1", pdf_path, tmp_path)
    assert ok is True
    assert (tmp_path / "doc1_thumb.png").exists()


def test_generate_thumbnail_pdf_no_pages(tmp_path):
    from unittest.mock import MagicMock, patch

    pdf_path = tmp_path / "empty.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n%%EOF")

    mock_doc = MagicMock()
    mock_doc.page_count = 0
    mock_doc.__enter__.return_value = mock_doc
    mock_doc.__exit__.return_value = False

    with patch("fitz.open", return_value=mock_doc):
        ok = generate_thumbnail("doc1", pdf_path, tmp_path)
    assert ok is False
    assert not (tmp_path / "doc1_thumb.png").exists()


def test_generate_thumbnail_text(tmp_path):
    txt_path = tmp_path / "notes.txt"
    txt_path.write_text("Hello world\n" * 30)

    ok = generate_thumbnail("doc2", txt_path, tmp_path)
    assert ok is True
    assert (tmp_path / "doc2_thumb.png").exists()


def test_generate_thumbnail_markdown(tmp_path):
    md_path = tmp_path / "notes.md"
    md_path.write_text("# Heading\n\nSome body text.")

    ok = generate_thumbnail("doc3", md_path, tmp_path)
    assert ok is True
    assert (tmp_path / "doc3_thumb.png").exists()


def test_generate_thumbnail_unsupported_extension(tmp_path):
    docx_path = tmp_path / "report.docx"
    docx_path.write_bytes(b"not a real docx")

    ok = generate_thumbnail("doc4", docx_path, tmp_path)
    assert ok is False
    assert not (tmp_path / "doc4_thumb.png").exists()


def test_generate_thumbnail_swallows_errors(tmp_path):
    missing_path = tmp_path / "does_not_exist.pdf"
    ok = generate_thumbnail("doc5", missing_path, tmp_path)
    assert ok is False
