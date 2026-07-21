"""Best-effort preview thumbnails for uploaded documents."""
from __future__ import annotations

from pathlib import Path

_THUMB_SIZE = (240, 320)  # roughly a page aspect ratio


def thumbnail_path(upload_folder: Path, doc_id: str) -> Path:
    return upload_folder / f"{doc_id}_thumb.png"


def generate_thumbnail(doc_id: str, file_path: Path, upload_folder: Path) -> bool:
    """Best-effort thumbnail generation. Returns True if a thumbnail was written."""
    out_path = thumbnail_path(upload_folder, doc_id)
    try:
        ext = file_path.suffix.lower()
        if ext == ".pdf":
            return _thumbnail_pdf(file_path, out_path)
        if ext in (".txt", ".md", ".csv"):
            return _thumbnail_text(file_path, out_path)
        return False
    except Exception:
        return False


def _thumbnail_pdf(file_path: Path, out_path: Path) -> bool:
    import fitz  # PyMuPDF

    with fitz.open(file_path) as doc:
        if doc.page_count == 0:
            return False
        page = doc[0]
        target_w, target_h = _THUMB_SIZE
        zoom = min(target_w / page.rect.width, target_h / page.rect.height)
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
        pix.save(out_path)
    return True


def _thumbnail_text(file_path: Path, out_path: Path) -> bool:
    from PIL import Image, ImageDraw, ImageFont

    text = file_path.read_text(encoding="utf-8", errors="ignore")
    img = Image.new("RGB", _THUMB_SIZE, "white")
    draw = ImageDraw.Draw(img)
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont
    try:
        font = ImageFont.truetype("arial.ttf", 9)
    except Exception:
        font = ImageFont.load_default()

    margin = 10
    chars_per_line = 38
    y = margin
    for raw_line in text.splitlines():
        line = raw_line if raw_line else " "
        while line:
            if y > _THUMB_SIZE[1] - margin:
                break
            chunk, line = line[:chars_per_line], line[chars_per_line:]
            draw.text((margin, y), chunk, fill="black", font=font)
            y += 11
        if y > _THUMB_SIZE[1] - margin:
            break

    img.save(out_path)
    return True
