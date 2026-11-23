"""Prepare a bot's spoken introduction and static Meet camera frame.

The camera shows an uploaded photo only after the owner verified their
likeness consent. Anonymous Meet bots still use an initial for their profile
icon; this frame is shown in the bot's video tile instead.
"""
from __future__ import annotations

import base64
import io
import logging

from PIL import Image, ImageDraw, ImageFont, ImageOps, UnidentifiedImageError

from coworker import blobstore, twin, voice
from coworker.store import Store

log = logging.getLogger("coworker.bot_media")


def greeting(store: Store, user_id: int, disclosure: str) -> str | None:
    """Synthesize the actual opener played to the meeting, or use chat only."""
    if not voice.is_configured():
        return None
    settings = (store.get_coworker(user_id) or {}).get("settings") or {}
    audio = voice.tts(disclosure, settings.get("voice_id"))
    if not audio:
        raise voice.VoiceError("Text-to-speech returned no greeting audio")
    return base64.b64encode(audio).decode("ascii")


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except OSError:
        return ImageFont.load_default()


def camera_frame(store: Store, user_id: int) -> str:
    """A compact 16:9 JPEG for Recall automatic_video_output."""
    image = Image.new("RGB", (1280, 720), "#171921")
    draw = ImageDraw.Draw(image)
    coworker = store.get_coworker(user_id) or {}
    first = ((coworker.get("owner_name") or "AI").split(" ")[0])[:32]
    photo = None
    if twin.verified(store, user_id, "video_likeness"):
        asset = next((a for a in reversed(twin.assets(store, user_id)) if a["kind"] == "photo"), None)
        if asset:
            try:
                raw = blobstore.get(asset["path"])
                with Image.open(io.BytesIO(raw)) as source:
                    oriented = ImageOps.exif_transpose(source)
                    if oriented is not None:
                        photo = ImageOps.fit(oriented.convert("RGB"), (400, 400))
            except (OSError, ValueError, UnidentifiedImageError):
                log.warning("Couldn't load the consented photo for meeting camera; using initials")
    draw.ellipse((437, 97, 843, 503), fill="#555874")
    if photo:
        mask = Image.new("L", (400, 400), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, 400, 400), fill=255)
        image.paste(photo, (440, 100), mask)
    else:
        initials = "".join(part[0].upper() for part in (coworker.get("owner_name") or "AI").split()[:2])
        draw.text((640, 300), initials, font=_font(145), fill="white", anchor="mm")
    draw.text((640, 555), f"{first}'s AI coworker", font=_font(42), fill="white", anchor="mm")
    draw.text((640, 635), "AI  ·  OUROGEN", font=_font(28), fill="#A9ABC2", anchor="mm")
    output = io.BytesIO()
    image.save(output, format="JPEG", quality=82, optimize=True)
    return base64.b64encode(output.getvalue()).decode("ascii")
