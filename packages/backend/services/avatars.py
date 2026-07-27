"""User profile picture storage — always normalized to a small PNG."""
from __future__ import annotations

import os
from pathlib import Path
from typing import IO

_AVATAR_DIR: Path = Path(os.environ.get("AVATAR_FOLDER", "/tmp/anote_avatars")).resolve()
_AVATAR_DIR.mkdir(parents=True, exist_ok=True)

AVATAR_FOLDER = _AVATAR_DIR
_MAX_DIMENSION = 256


def avatar_path(user_id: int) -> Path:
    return AVATAR_FOLDER / f"{user_id}.png"


def save_avatar(user_id: int, file_stream: IO[bytes]) -> None:
    """Normalize an uploaded image to a small square-ish PNG."""
    from PIL import Image

    img = Image.open(file_stream).convert("RGB")
    img.thumbnail((_MAX_DIMENSION, _MAX_DIMENSION))
    img.save(avatar_path(user_id), format="PNG")


def delete_avatar(user_id: int) -> bool:
    path = avatar_path(user_id)
    if path.exists():
        path.unlink()
        return True
    return False
