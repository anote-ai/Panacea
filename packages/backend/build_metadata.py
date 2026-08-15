"""Build metadata shared by health and version endpoints."""
from __future__ import annotations

import os

DEFAULT_VERSION = "1.0.0"
UNKNOWN_COMMIT = "unknown"

_COMMIT_ENV_VARS = (
    "PANACEA_BUILD_SHA",
    "GITHUB_SHA",
    "COMMIT_SHA",
    "SOURCE_VERSION",
)


def get_build_metadata() -> dict[str, str]:
    """Return public, non-secret metadata identifying the running build."""
    commit = next(
        (os.environ[name].strip() for name in _COMMIT_ENV_VARS if os.environ.get(name, "").strip()),
        UNKNOWN_COMMIT,
    )
    version = os.environ.get("PANACEA_VERSION", DEFAULT_VERSION).strip() or DEFAULT_VERSION
    return {
        "service": "anote-backend",
        "version": version,
        "commit": commit,
    }
