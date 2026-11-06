"""Run the repository's own tests against the engineer's changes, isolated from this server.

The demo repo always runs (it's our own fixture code). Real repositories run
only when ``COWORKER_SANDBOX=1``: that clones the repo into a temp directory,
overlays the changed files, and runs the test command with a stripped
environment and a timeout. Run the worker in its own container when you turn
this on; it executes the repository's code.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from typing import Any

from coworker.connectors.devtools_demo import FILES as DEMO_FILES
from coworker.connectors.devtools_demo import REPO as DEMO_REPO

TIMEOUT = int(os.environ.get("COWORKER_SANDBOX_TIMEOUT", "300"))
SAFE_ENV = ("PATH", "HOME", "LANG", "LC_ALL", "TMPDIR", "PYTHONHASHSEED")


def enabled(repo: str) -> bool:
    return repo == DEMO_REPO or os.environ.get("COWORKER_SANDBOX") == "1"


def detect_command(paths: list[str], override: str = "") -> list[str]:
    if override:
        return override.split()
    if any(p.endswith(".py") for p in paths):
        return [sys.executable, "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider"]
    if "package.json" in paths:
        return ["npm", "test", "--silent"]
    if "go.mod" in paths:
        return ["go", "test", "./..."]
    if "Cargo.toml" in paths:
        return ["cargo", "test", "--quiet"]
    return []


def _write(root: str, files: dict[str, str | None]) -> None:
    for path, content in files.items():
        target = os.path.realpath(os.path.join(root, path))
        if not target.startswith(os.path.realpath(root) + os.sep):
            raise ValueError(f"{path} is outside the repository")
        if content is None:
            if os.path.exists(target):
                os.remove(target)
            continue
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "w") as fh:
            fh.write(content)


def _clone(repo: str, token: str, dest: str) -> None:
    url = f"https://x-access-token:{token}@github.com/{repo}.git" if token else f"https://github.com/{repo}.git"
    subprocess.run(["git", "clone", "--depth", "1", "--quiet", url, dest], check=True, capture_output=True,
                   timeout=TIMEOUT, env={k: os.environ[k] for k in SAFE_ENV if k in os.environ})


def run(repo: str, changes: dict[str, str | None], *, token: str = "", command: str = "",
        extra_files: dict[str, str] | None = None) -> dict[str, Any]:
    """Apply ``changes`` (path → new content, None = delete) and run the tests."""
    if not enabled(repo):
        return {"ran": False, "passed": None, "output": "Sandbox is off for real repositories (COWORKER_SANDBOX=1 turns it on).",
                "command": ""}
    root = tempfile.mkdtemp(prefix="cw-sandbox-")
    try:
        if repo == DEMO_REPO:
            _write(root, dict(DEMO_FILES))
        else:
            _clone(repo, token, os.path.join(root, "repo"))
            root = os.path.join(root, "repo")
        _write(root, changes)
        if extra_files:
            _write(root, dict(extra_files))
        paths = [os.path.relpath(os.path.join(d, f), root) for d, _, fs in os.walk(root) for f in fs
                 if ".git" not in d.split(os.sep)]
        cmd = detect_command(paths, command)
        if not cmd:
            return {"ran": False, "passed": None, "output": "No test command found.", "command": ""}
        env = {k: os.environ[k] for k in SAFE_ENV if k in os.environ}
        try:
            proc = subprocess.run(cmd, cwd=root, capture_output=True, text=True, timeout=TIMEOUT, env=env)
        except subprocess.TimeoutExpired:
            return {"ran": True, "passed": False, "output": f"Timed out after {TIMEOUT}s", "command": " ".join(cmd)}
        except FileNotFoundError:
            return {"ran": False, "passed": None, "output": f"{cmd[0]} isn't installed here.", "command": " ".join(cmd)}
        output = (proc.stdout + proc.stderr)[-6000:]
        return {"ran": True, "passed": proc.returncode == 0, "output": output, "command": " ".join(cmd[-4:])}
    except subprocess.CalledProcessError:  # the clone; never echo the command, it holds the token
        return {"ran": False, "passed": None, "output": f"Couldn't clone {repo}.", "command": ""}
    except subprocess.SubprocessError as exc:  # e.g. the clone timed out; the message would hold the token
        return {"ran": False, "passed": None, "output": f"Sandbox error: {type(exc).__name__}", "command": ""}
    except (OSError, ValueError) as exc:
        return {"ran": False, "passed": None, "output": f"Sandbox error: {exc}"[:2000], "command": ""}
    finally:
        shutil.rmtree(root.removesuffix(os.sep + "repo") if root.endswith(os.sep + "repo") else root, ignore_errors=True)
