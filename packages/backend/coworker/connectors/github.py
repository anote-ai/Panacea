"""GitHub: where the AI engineer reads code and history, and opens pull requests.

Two ways to connect:

* OAuth (``GITHUB_CLIENT_ID`` / ``GITHUB_CLIENT_SECRET``) from a GitHub OAuth app.
* Paste a personal access token (classic ``ghp_…`` or fine-grained ``github_pat_…``)
  with read access to the repositories and, for writes, Contents, Issues and
  Pull requests write access.

Sync reads what the owner did: pull requests they authored (with the files they
touched), review comments they left, and issues they're involved in. That's the
raw material for the knowledge pack. Writes (comment, issue, review, pull
request) only ever run as approved actions.
"""
from __future__ import annotations

import base64
import os
import time
from typing import Any
from urllib.parse import urlencode

import requests

from coworker.connectors.base import ConnectorError
from coworker.store import Store, iso

API = os.environ.get("GITHUB_API_URL", "https://api.github.com").rstrip("/")
OAUTH = "https://github.com/login/oauth"
SCOPES = ["repo", "read:user"]
TIMEOUT = 20
SYNC_PRS = 30
SYNC_REVIEWS = 15
SYNC_ISSUES = 30


def is_configured() -> bool:
    return bool(os.environ.get("GITHUB_CLIENT_ID") and os.environ.get("GITHUB_CLIENT_SECRET"))


def redirect_uri() -> str:
    default = f"{os.environ.get('BACKEND_URL', 'http://localhost:5000').rstrip('/')}/api/coworker/connections/github/callback"
    return os.environ.get("GITHUB_REDIRECT_URI", default)


def auth_url(state: str) -> str:
    return f"{OAUTH}/authorize?" + urlencode({
        "client_id": os.environ.get("GITHUB_CLIENT_ID", ""), "redirect_uri": redirect_uri(),
        "scope": " ".join(SCOPES), "state": state, "allow_signup": "false",
    })


def exchange_code(code: str) -> dict[str, Any]:
    resp = requests.post(f"{OAUTH}/access_token", data={
        "client_id": os.environ.get("GITHUB_CLIENT_ID", ""), "client_secret": os.environ.get("GITHUB_CLIENT_SECRET", ""),
        "code": code, "redirect_uri": redirect_uri(),
    }, headers={"Accept": "application/json"}, timeout=TIMEOUT)
    body: dict[str, Any] = resp.json() if resp.content else {}
    if resp.status_code >= 400 or not body.get("access_token"):
        raise ConnectorError(f"GitHub sign-in failed: {body.get('error_description') or resp.status_code}", "oauth_failed")
    token = {"kind": "oauth", "access_token": body["access_token"], "scope": body.get("scope", "")}
    token["login"] = GitHubClient(token).login()
    return token


def verify_token(value: str) -> dict[str, Any]:
    token: dict[str, Any] = {"kind": "pat", "access_token": value}
    token["login"] = GitHubClient(token).login()
    return token


def looks_like_token(value: str) -> bool:
    return value.startswith(("ghp_", "github_pat_", "gho_")) and len(value) >= 20


def revoke(token: dict[str, Any]) -> None:
    if token.get("kind") != "oauth" or not is_configured():
        return
    try:
        requests.delete(f"{API}/applications/{os.environ['GITHUB_CLIENT_ID']}/grant",
                        auth=(os.environ["GITHUB_CLIENT_ID"], os.environ["GITHUB_CLIENT_SECRET"]),
                        json={"access_token": token.get("access_token", "")}, timeout=TIMEOUT)
    except requests.RequestException:
        pass


def _split(repo: str) -> str:
    repo = repo.strip().removeprefix("https://github.com/").strip("/")
    if repo.count("/") != 1:
        raise ConnectorError(f"'{repo}' isn't a repository. Use owner/name.", "bad_request")
    return repo


class GitHubClient:
    label = "GitHub"
    provider = "github"

    def __init__(self, token: dict[str, Any], on_refresh: Any = None) -> None:
        self.token = token
        self._login = str(token.get("login") or "")

    # -- transport -----------------------------------------------------------

    def request(self, method: str, path: str, allow_404: bool = False, **kwargs: Any) -> Any:
        headers = {"Authorization": f"Bearer {self.token.get('access_token', '')}",
                   "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
        for attempt in range(3):
            resp = requests.request(method, f"{API}{path}", headers=headers, timeout=TIMEOUT, **kwargs)
            limited = resp.status_code in (403, 429) and resp.headers.get("X-RateLimit-Remaining") == "0"
            if (resp.status_code == 429 or limited) and attempt < 2:
                time.sleep(min(float(resp.headers.get("Retry-After", "1")), 5))
                continue
            if allow_404 and resp.status_code == 404:
                return None
            body = resp.json() if resp.content else {}
            if resp.status_code >= 400:
                code = "reauth_required" if resp.status_code == 401 else "provider_error"
                message = body.get("message") if isinstance(body, dict) else ""
                raise ConnectorError(f"GitHub {method} {path} failed: {message or resp.status_code}", code)
            return body
        raise ConnectorError("GitHub is rate limiting requests. Try again in a minute.", "rate_limited")  # pragma: no cover

    def login(self) -> str:
        if not self._login:
            self._login = str(self.request("GET", "/user").get("login") or "")
        return self._login

    # -- reads -----------------------------------------------------------------

    def _search(self, query: str, limit: int) -> list[dict[str, Any]]:
        body = self.request("GET", "/search/issues", params={"q": query, "sort": "updated", "order": "desc",
                                                             "per_page": limit})
        return list(body.get("items") or [])

    def pr_files(self, repo: str, number: int) -> list[dict[str, Any]]:
        files = self.request("GET", f"/repos/{_split(repo)}/pulls/{number}/files", params={"per_page": 100})
        return [{"path": f.get("filename", ""), "status": f.get("status", ""), "additions": f.get("additions", 0),
                 "deletions": f.get("deletions", 0), "patch": f.get("patch", "")} for f in files or []]

    def pull(self, repo: str, number: int) -> dict[str, Any]:
        pr = self.request("GET", f"/repos/{_split(repo)}/pulls/{number}")
        return {"number": number, "title": pr.get("title", ""), "body": pr.get("body") or "",
                "base": (pr.get("base") or {}).get("ref", ""), "head": (pr.get("head") or {}).get("ref", ""),
                "head_sha": (pr.get("head") or {}).get("sha", ""), "author": (pr.get("user") or {}).get("login", ""),
                "url": pr.get("html_url", "")}

    def read_file(self, repo: str, path: str, ref: str = "") -> str | None:
        params = {"ref": ref} if ref else {}
        body = self.request("GET", f"/repos/{_split(repo)}/contents/{path.lstrip('/')}", allow_404=True, params=params)
        if not body or isinstance(body, list) or body.get("encoding") != "base64":
            return None
        return base64.b64decode(body.get("content", "")).decode("utf-8", errors="replace")

    def tree(self, repo: str, ref: str = "") -> list[str]:
        repo = _split(repo)
        ref = ref or self.default_branch(repo)
        body = self.request("GET", f"/repos/{repo}/git/trees/{ref}", params={"recursive": "1"})
        return [t["path"] for t in body.get("tree") or [] if t.get("type") == "blob"]

    def default_branch(self, repo: str) -> str:
        return str(self.request("GET", f"/repos/{_split(repo)}").get("default_branch") or "main")

    def sync(self, store: Store, user_id: int) -> int:
        """Store the owner's recent PRs (with files), review comments, and issues as items."""
        me = self.login()
        count = 0
        for pr in self._search(f"author:{me} type:pr", SYNC_PRS):
            repo = _repo_of(pr)
            files = []
            try:
                files = [{k: f[k] for k in ("path", "status", "additions", "deletions")}
                         for f in self.pr_files(repo, pr["number"])]
            except ConnectorError:
                pass
            count += _add(store, user_id, "pull_request", f"pr:{repo}#{pr['number']}", pr, repo, me,
                          {"files": files, "merged": bool((pr.get("pull_request") or {}).get("merged_at"))})
        for pr in self._search(f"reviewed-by:{me} type:pr -author:{me}", SYNC_REVIEWS):
            repo = _repo_of(pr)
            try:
                comments = self.request("GET", f"/repos/{repo}/pulls/{pr['number']}/comments", params={"per_page": 100})
            except ConnectorError:
                continue
            for c in comments or []:
                if (c.get("user") or {}).get("login") != me:
                    continue
                count += bool(store.add_item(user_id, {
                    "provider": "github", "external_id": f"review:{c.get('id')}", "kind": "review_comment",
                    "thread_id": f"github:{repo}#{pr['number']}", "direction": "outbound", "author_name": me,
                    "subject": pr.get("title", "")[:500], "body": c.get("body") or "", "channel": repo,
                    "occurred_at": c.get("created_at") or iso(),
                    "meta": {"url": c.get("html_url", ""), "path": c.get("path", ""), "diff_hunk": (c.get("diff_hunk") or "")[-600:]},
                }))
        for issue in self._search(f"involves:{me} type:issue", SYNC_ISSUES):
            count += _add(store, user_id, "issue", f"issue:{_repo_of(issue)}#{issue['number']}", issue,
                          _repo_of(issue), me, {"state": issue.get("state", "")})
        return count

    # -- writes (run only as approved actions) ---------------------------------

    def comment(self, repo: str, number: int, body: str) -> dict[str, Any]:
        out = self.request("POST", f"/repos/{_split(repo)}/issues/{number}/comments", json={"body": body})
        return {"external_id": str(out.get("id", "")), "url": out.get("html_url", ""),
                "undo": {"provider": "github", "op": "delete_comment", "repo": repo, "id": out.get("id")}}

    def create_issue(self, repo: str, title: str, body: str, labels: list[str] | None = None) -> dict[str, Any]:
        out = self.request("POST", f"/repos/{_split(repo)}/issues", json={"title": title, "body": body,
                                                                          "labels": labels or []})
        return {"external_id": str(out.get("number", "")), "url": out.get("html_url", ""),
                "undo": {"provider": "github", "op": "close_issue", "repo": repo, "number": out.get("number")}}

    def review(self, repo: str, number: int, body: str, comments: list[dict[str, Any]],
               event: str = "COMMENT") -> dict[str, Any]:
        payload: dict[str, Any] = {"body": body, "event": event if event in ("COMMENT", "REQUEST_CHANGES") else "COMMENT",
                                   "comments": [{"path": c["path"], "line": int(c["line"]), "side": "RIGHT",
                                                 "body": c["body"]} for c in comments if c.get("path") and c.get("line")]}
        out = self.request("POST", f"/repos/{_split(repo)}/pulls/{number}/reviews", json=payload)
        return {"external_id": str(out.get("id", "")), "url": out.get("html_url", ""), "undo": {}}

    def open_pr(self, repo: str, *, branch: str, title: str, body: str, files: list[dict[str, Any]],
                base: str = "") -> dict[str, Any]:
        """One commit with every file change on a new branch, then a pull request into ``base``."""
        repo = _split(repo)
        base = base or self.default_branch(repo)
        base_sha = self.request("GET", f"/repos/{repo}/git/ref/heads/{base}")["object"]["sha"]
        base_tree = self.request("GET", f"/repos/{repo}/git/commits/{base_sha}")["tree"]["sha"]
        entries = []
        for f in files:
            if f.get("delete"):
                entries.append({"path": f["path"], "mode": "100644", "type": "blob", "sha": None})
            else:
                entries.append({"path": f["path"], "mode": "100644", "type": "blob", "content": f.get("content", "")})
        new_tree = self.request("POST", f"/repos/{repo}/git/trees", json={"base_tree": base_tree, "tree": entries})["sha"]
        commit = self.request("POST", f"/repos/{repo}/git/commits", json={
            "message": title, "tree": new_tree, "parents": [base_sha]})["sha"]
        self.request("POST", f"/repos/{repo}/git/refs", json={"ref": f"refs/heads/{branch}", "sha": commit})
        pr = self.request("POST", f"/repos/{repo}/pulls", json={"title": title, "body": body, "head": branch, "base": base})
        return {"external_id": str(pr.get("number", "")), "url": pr.get("html_url", ""), "branch": branch, "base": base,
                "undo": {"provider": "github", "op": "close_pr", "repo": repo, "number": pr.get("number"), "branch": branch}}

    def undo(self, info: dict[str, Any]) -> bool:
        repo = info.get("repo", "")
        if info.get("op") == "delete_comment":
            self.request("DELETE", f"/repos/{_split(repo)}/issues/comments/{info['id']}")
            return True
        if info.get("op") == "close_issue":
            self.request("PATCH", f"/repos/{_split(repo)}/issues/{info['number']}", json={"state": "closed"})
            return True
        if info.get("op") == "close_pr":
            self.request("PATCH", f"/repos/{_split(repo)}/pulls/{info['number']}", json={"state": "closed"})
            self.request("DELETE", f"/repos/{_split(repo)}/git/refs/heads/{info['branch']}", allow_404=True)
            return True
        return False


def _repo_of(item: dict[str, Any]) -> str:
    url = str(item.get("repository_url") or "")
    return "/".join(url.rstrip("/").split("/")[-2:])


def _add(store: Store, user_id: int, kind: str, external_id: str, item: dict[str, Any], repo: str, me: str,
         meta: dict[str, Any]) -> int:
    return int(bool(store.add_item(user_id, {
        "provider": "github", "external_id": external_id, "kind": kind,
        "thread_id": f"github:{repo}#{item.get('number')}",
        "direction": "outbound" if (item.get("user") or {}).get("login") == me else "inbound",
        "author_name": (item.get("user") or {}).get("login", ""), "subject": (item.get("title") or "")[:500],
        "body": item.get("body") or "", "channel": repo, "occurred_at": item.get("updated_at") or iso(),
        "meta": {"url": item.get("html_url", ""), "labels": [lb.get("name") for lb in item.get("labels") or []], **meta},
    })))
