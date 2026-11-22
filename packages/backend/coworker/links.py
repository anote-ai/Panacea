"""Recognize meeting links by their real hostname.

Substring checks such as ``"meet.google.com" in url`` also accept
``https://evil.example/?meet.google.com`` or ``https://meet.google.com.evil.example``.
These helpers parse the URL and compare the hostname (or a parent domain).
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

_PLATFORMS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("zoom", ("zoom.us",)),
    ("google_meet", ("meet.google.com",)),
    ("teams", ("teams.microsoft.com", "teams.live.com")),
)
# Each match starts at "https://" and runs to the next whitespace, so
# scanning is linear in the text length.
_URL = re.compile(r"https://[^\s]+", re.IGNORECASE)


def hostname(url: str) -> str:
    try:
        return (urlparse(url if "://" in url else f"https://{url}").hostname or "").lower()
    except ValueError:
        return ""


def on_domain(host: str, domain: str) -> bool:
    return host == domain or host.endswith("." + domain)


def platform(url: str) -> str:
    if not url:
        return "browser"
    host = hostname(url)
    for name, domains in _PLATFORMS:
        if any(on_domain(host, d) for d in domains):
            return name
    return "other"


def has_meeting_link(text: str) -> bool:
    return any(platform(u) != "other" for u in _URL.findall(text or ""))
