"""Tests for the workspace API — hosted-mode CRUD and git clone paths.

The blueprint computes HOSTED_MODE at import time from ANOTE_MODE, so these
tests monkeypatch the module-level flag (and the in-memory store) to exercise
the hosted-only branches that the default non-hosted config never reaches.
"""
from __future__ import annotations

import subprocess

import pytest

from api_endpoints.workspaces import handler as ws_handler


@pytest.fixture
def hosted(monkeypatch, tmp_path):
    """Enable hosted mode with an isolated workspace dir and empty store."""
    monkeypatch.setattr(ws_handler, "HOSTED_MODE", True)
    monkeypatch.setattr(ws_handler, "WORKSPACES_DIR", tmp_path)
    monkeypatch.setattr(ws_handler, "_workspaces", {})


def test_list_empty(client, hosted):
    resp = client.get("/api/workspaces")
    assert resp.status_code == 200
    assert resp.get_json() == {"workspaces": []}


def test_create_requires_name(client, hosted):
    resp = client.post("/api/workspaces", json={})
    assert resp.status_code == 400


def test_create_and_list(client, hosted):
    resp = client.post("/api/workspaces", json={"name": "my-project"})
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["name"] == "my-project"
    ws_id = body["id"]

    listed = client.get("/api/workspaces").get_json()["workspaces"]
    assert any(w["id"] == ws_id for w in listed)


def test_get_workspace(client, hosted):
    ws_id = client.post("/api/workspaces", json={"name": "w"}).get_json()["id"]
    resp = client.get(f"/api/workspaces/{ws_id}")
    assert resp.status_code == 200
    assert resp.get_json()["id"] == ws_id


def test_get_workspace_not_found(client, hosted):
    resp = client.get("/api/workspaces/does-not-exist")
    assert resp.status_code == 404


def test_delete_workspace(client, hosted):
    ws_id = client.post("/api/workspaces", json={"name": "w"}).get_json()["id"]
    resp = client.delete(f"/api/workspaces/{ws_id}")
    assert resp.status_code == 200
    assert resp.get_json()["deleted"] is True
    # Second delete now 404s — it's gone from the store.
    assert client.delete(f"/api/workspaces/{ws_id}").status_code == 404


def test_delete_workspace_not_found(client, hosted):
    resp = client.delete("/api/workspaces/nope")
    assert resp.status_code == 404


def test_clone_not_found(client, hosted):
    resp = client.post("/api/workspaces/nope/clone", json={"repoUrl": "https://x/y.git"})
    assert resp.status_code == 404


def test_clone_requires_repo_url(client, hosted):
    ws_id = client.post("/api/workspaces", json={"name": "w"}).get_json()["id"]
    resp = client.post(f"/api/workspaces/{ws_id}/clone", json={})
    assert resp.status_code == 400


def test_clone_success(client, hosted, monkeypatch):
    ws_id = client.post("/api/workspaces", json={"name": "w"}).get_json()["id"]

    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(args, 0, b"", b"")

    monkeypatch.setattr(subprocess, "run", fake_run)
    resp = client.post(
        f"/api/workspaces/{ws_id}/clone", json={"repoUrl": "https://github.com/x/y.git"}
    )
    assert resp.status_code == 200
    assert resp.get_json()["cloned"] is True


def test_clone_git_failure(client, hosted, monkeypatch):
    ws_id = client.post("/api/workspaces", json={"name": "w"}).get_json()["id"]

    def fake_run(*args, **kwargs):
        raise subprocess.CalledProcessError(1, "git", stderr=b"fatal: repo not found")

    monkeypatch.setattr(subprocess, "run", fake_run)
    resp = client.post(
        f"/api/workspaces/{ws_id}/clone", json={"repoUrl": "https://github.com/x/y.git"}
    )
    assert resp.status_code == 500
    assert "repo not found" in resp.get_json()["error"]


def test_all_endpoints_blocked_in_non_hosted(client):
    """Without hosted mode every workspace route returns 501."""
    assert client.get("/api/workspaces").status_code == 501
    assert client.post("/api/workspaces", json={"name": "w"}).status_code == 501
    assert client.get("/api/workspaces/x").status_code == 501
    assert client.delete("/api/workspaces/x").status_code == 501
    assert client.post("/api/workspaces/x/clone", json={}).status_code == 501
