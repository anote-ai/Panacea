"""Coding workspace endpoints — connect a GitHub repo and browse its files."""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import uuid
from pathlib import Path

from flask import Blueprint, jsonify, request

coding_bp = Blueprint("coding", __name__, url_prefix="/api/coding")

CODING_WORKSPACES_DIR = Path(os.environ.get("CODING_WORKSPACES_DIR", "/tmp/anote_coding_workspaces"))
CODING_WORKSPACES_DIR.mkdir(parents=True, exist_ok=True)

# Only plain github.com HTTPS repo URLs — prevents git-clone from being used
# as an SSRF/local-file-read vector via file://, internal hosts, etc.
_GITHUB_URL_RE = re.compile(
    r"^https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:\.git)?/?$"
)

_MAX_FILE_BYTES = 1_000_000  # 1MB cap on raw file content returned to the viewer

_repos: dict[str, dict] = {}  # repoId -> {"path": str, "repoUrl": str}


def _build_tree(root: Path, current: Path) -> dict:
    """Recursively build a JSON-serializable file tree, excluding .git."""
    rel = current.relative_to(root)
    children: list[dict] = []
    for child in sorted(current.iterdir(), key=lambda p: (p.is_file(), p.name.lower())):
        if child.name == ".git":
            continue
        if child.is_dir():
            children.append(_build_tree(root, child))
        else:
            child_rel = child.relative_to(root)
            children.append({"name": child.name, "path": str(child_rel), "type": "file"})
    return {
        "name": current.name if rel != Path(".") else root.name,
        "path": "" if rel == Path(".") else str(rel),
        "type": "dir",
        "children": children,
    }


@coding_bp.post("/connect-repo")
def connect_repo() -> tuple:  # type: ignore[type-arg]
    data = request.get_json(silent=True) or {}
    repo_url = data.get("repoUrl", "").strip()
    if not repo_url:
        return jsonify({"error": "repoUrl is required"}), 400
    if not _GITHUB_URL_RE.match(repo_url):
        return jsonify({"error": "Only https://github.com/<owner>/<repo> URLs are supported"}), 400

    repo_id = str(uuid.uuid4())
    repo_path = CODING_WORKSPACES_DIR / repo_id
    repo_path.mkdir(parents=True, exist_ok=True)

    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", repo_url, "."],
            cwd=str(repo_path),
            capture_output=True,
            timeout=60,
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        shutil.rmtree(repo_path, ignore_errors=True)
        stderr = exc.stderr.decode(errors="ignore")[:500] if exc.stderr else "git clone failed"
        return jsonify({"error": f"Failed to clone repo: {stderr}"}), 502
    except subprocess.TimeoutExpired:
        shutil.rmtree(repo_path, ignore_errors=True)
        return jsonify({"error": "Cloning the repo timed out"}), 504

    _repos[repo_id] = {"path": str(repo_path), "repoUrl": repo_url}
    tree = _build_tree(repo_path, repo_path)
    tree["name"] = repo_url.rstrip("/").removesuffix(".git").rsplit("/", 1)[-1]
    return jsonify({"repoId": repo_id, "repoUrl": repo_url, "tree": tree}), 200


@coding_bp.get("/repos/<repo_id>/file")
def get_file(repo_id: str) -> tuple:  # type: ignore[type-arg]
    repo = _repos.get(repo_id)
    if not repo:
        return jsonify({"error": "Repo not found. Connect it again."}), 404

    rel_path = request.args.get("path", "")
    if not rel_path:
        return jsonify({"error": "path query param is required"}), 400

    repo_root = Path(repo["path"]).resolve()
    target = (repo_root / rel_path).resolve()

    # Reject path traversal outside the cloned repo directory
    if repo_root not in target.parents and target != repo_root:
        return jsonify({"error": "Invalid path"}), 400
    if not target.is_file():
        return jsonify({"error": "File not found"}), 404

    raw = target.read_bytes()
    if b"\x00" in raw[:8000]:
        return jsonify({"error": "Binary file preview is not supported yet"}), 415

    content = raw[:_MAX_FILE_BYTES].decode("utf-8", errors="replace")
    truncated = len(raw) > _MAX_FILE_BYTES
    return jsonify({"path": rel_path, "content": content, "truncated": truncated}), 200
