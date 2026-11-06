"""The AI engineer: spec → task graph → auto-prompted coding → checks → review → pull request.

A run moves through these statuses:

* ``spec``: drafted from chat or a ticket; the human confirms or edits it.
* ``planned``: the task graph is built; the human can edit it, then starts the run.
* ``running``: each layer of the graph runs (independent tasks in parallel). Each
  task is a prompt built from the repo, the owner's knowledge pack, and the
  acceptance criteria. The repo's tests run in a sandbox; failures go back to
  the model with what went wrong (up to ``MAX_FIX_ATTEMPTS``).
* ``ready``: the AI code reviewer and slop checks ran, and a ``github.pr`` action
  waits for approval (or runs, if autonomy allows and nothing was flagged).
* ``pr_opened`` / ``failed`` / ``needs_model`` (offline, outside the demo).

Nothing is pushed until the ``github.pr`` action is approved.
"""
from __future__ import annotations

import contextvars
import json
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from coworker import knowledge_pack, llm
from coworker.connectors import devtools
from coworker.connectors.devtools_demo import REPO as DEMO_REPO
from coworker.engineering import diffs, graph, review, sandbox, slop
from coworker.engineering import spec as specs
from coworker.engineering.demo import DEMO_SOLUTION
from coworker.store import Store, iso

MAX_FIX_ATTEMPTS = 2
MAX_CONTEXT_FILES = 12
DEFAULT_MIN_SLOP = 70
NEEDS_MODEL = ("The engineer needs a model to write code. Add an API key in Settings → Models, or run a free local "
               "model with Ollama. (The demo repo works without one.)")


class RunError(Exception):
    def __init__(self, message: str, code: str = "bad_request") -> None:
        super().__init__(message)
        self.code = code


def _get(store: Store, user_id: int, run_id: int) -> dict[str, Any]:
    run = store.get("cw_eng_runs", run_id, user_id)
    if not run:
        raise RunError("No such run", "not_found")
    return run


def _set(store: Store, user_id: int, run_id: int, **values: Any) -> dict[str, Any]:
    store.update("cw_eng_runs", run_id, user_id, {**values, "updated_at": iso()})
    return _get(store, user_id, run_id)


# -- 1. spec ------------------------------------------------------------------------

def create(store: Store, user_id: int, *, text: str = "", source: str = "", repo: str = "") -> dict[str, Any]:
    try:
        spec = specs.make(store, user_id, text=text, source=source, repo=repo)
    except ValueError as exc:
        raise RunError(str(exc)) from exc
    run_id = store.insert("cw_eng_runs", {
        "user_id": user_id, "title": spec["goal"][:500], "status": "spec", "source": source[:255],
        "repo": spec.get("repo", "")[:255], "spec": spec, "graph": [], "nodes": {}, "checks": {}, "slop": {}, "pr": {},
        "created_at": iso(), "updated_at": iso()})
    store.log(user_id, "engineer", f"Drafted a spec: {spec['goal']}", {"run_id": run_id})
    return _get(store, user_id, run_id)


def update_spec(store: Store, user_id: int, run_id: int, changes: dict[str, Any]) -> dict[str, Any]:
    run = _get(store, user_id, run_id)
    if run["status"] not in ("spec", "planned"):
        raise RunError("The spec can't change once the run has started", "conflict")
    merged = {**(run.get("spec") or {}), **{k: v for k, v in changes.items()
                                           if k in ("goal", "acceptance_criteria", "constraints", "repo")}}
    return _set(store, user_id, run_id, spec=merged, title=str(merged.get("goal", ""))[:500],
                repo=str(merged.get("repo", ""))[:255], status="spec", graph=[])


# -- 2. graph -----------------------------------------------------------------------

MAX_SCAN = 60


def _read_code(client: Any, repo: str, files: list[str]) -> dict[str, str]:
    """Read the code files most likely to matter (shallow paths first), for ranking and context."""
    code = sorted((p for p in files if diffs.is_code(p) and not diffs.is_test(p)), key=lambda p: (p.count("/"), p))
    return {p: c for p in code[:MAX_SCAN] if (c := client.read_file(repo, p)) is not None}

def _repo_context(store: Store, user_id: int, repo: str) -> tuple[Any, list[str]]:
    client = devtools.require(store, user_id, "github")
    try:
        return client, client.tree(repo)
    except Exception as exc:
        raise RunError(f"Couldn't read {repo}: {exc}", "provider_error") from exc


def plan(store: Store, user_id: int, run_id: int) -> dict[str, Any]:
    """Confirm the spec and build the task graph."""
    run = _get(store, user_id, run_id)
    if run["status"] not in ("spec", "planned"):
        raise RunError("This run is already underway", "conflict")
    try:
        spec = specs.validate(run.get("spec") or {})
    except ValueError as exc:
        raise RunError(str(exc)) from exc
    client, files = _repo_context(store, user_id, spec["repo"])
    contents = _read_code(client, spec["repo"], files)
    contents = {p: contents[p] for p in graph.rank_files(spec, files, contents)[:MAX_CONTEXT_FILES]}
    nodes = graph.plan(spec, files, contents, user_id=user_id)
    store.log(user_id, "engineer", f"Planned {len(nodes)} task(s) for: {spec['goal']}", {"run_id": run_id})
    return _set(store, user_id, run_id, spec=spec, graph=nodes, status="planned",
                nodes={n["id"]: {"status": "pending"} for n in nodes})


def update_graph(store: Store, user_id: int, run_id: int, nodes: list[dict[str, Any]]) -> dict[str, Any]:
    run = _get(store, user_id, run_id)
    if run["status"] != "planned":
        raise RunError("The graph can only change before the run starts", "conflict")
    try:
        clean = graph.validate(nodes)
    except graph.GraphError as exc:
        raise RunError(str(exc)) from exc
    return _set(store, user_id, run_id, graph=clean, nodes={n["id"]: {"status": "pending"} for n in clean})


# -- 3. auto-prompting --------------------------------------------------------------

def build_prompt(spec: dict[str, Any], node: dict[str, Any], files: dict[str, str | None], tree: list[str],
                 pack: dict[str, Any], failure: str = "") -> tuple[str, str]:
    criteria = spec["acceptance_criteria"]
    wanted = [criteria[i] for i in node.get("criteria") or [] if i < len(criteria)] or criteria
    shown = "\n\n".join(f"--- {p}\n{c if c is not None else '(new file)'}" for p, c in files.items())[:60000]
    system = ("You are a senior engineer working in the owner's repository, the way the owner works. "
              "Make the smallest change that meets the criteria. Never skip or weaken a test. Don't invent APIs; "
              "only use what the repository or its dependencies provide.")
    user = (f"GOAL: {spec['goal']}\nACCEPTANCE CRITERIA:\n" + "\n".join(f"- {c}" for c in wanted) +
            ("\nCONSTRAINTS:\n" + "\n".join(f"- {c}" for c in spec.get("constraints") or []) if spec.get("constraints") else "") +
            f"\n\nYOUR TASK ({node['kind']}): {node['title']}\nFILES YOU MAY CHANGE: {', '.join(node['files']) or 'any'}\n\n"
            f"{knowledge_pack.prompt_context(pack)}\n\nREPOSITORY TREE (partial):\n" + "\n".join(tree[:300]) +
            f"\n\nCURRENT FILES:\n{shown}\n" +
            (f"\nTHE LAST ATTEMPT FAILED. Fix it:\n{failure[-4000:]}\n" if failure else "") +
            "\nReturn JSON only: {\"files\": [{\"path\": str, \"content\": full new file text} or "
            "{\"path\": str, \"delete\": true}], \"notes\": str, \"pack_refs\": [ids from the list above you followed]}")
    return system, user


def _parse_files(text: str) -> dict[str, Any]:
    data = json.loads(text[text.find("{"): text.rfind("}") + 1])
    out = []
    for f in data.get("files") or []:
        path = str(f.get("path", "")).strip().lstrip("/")
        if not path or ".." in path.split("/"):
            continue
        out.append({"path": path, "delete": bool(f.get("delete")), "content": str(f.get("content", ""))})
    return {"files": out, "notes": str(data.get("notes", ""))[:2000],
            "pack_refs": [str(r) for r in data.get("pack_refs") or []][:20]}


def _demo_applies(spec: dict[str, Any]) -> bool:
    return spec["repo"] == DEMO_REPO and bool(re.search(r"\bannual|yearly\b", spec["goal"], re.I))


def _write_node(spec: dict[str, Any], node: dict[str, Any], working: dict[str, str | None], tree: list[str],
                pack: dict[str, Any], user_id: int, failure: str = "") -> dict[str, Any]:
    if not llm.available(user_id):
        if _demo_applies(spec) and node["kind"] in DEMO_SOLUTION:
            refs = [r["id"] for r in pack.get("style_rules") or [] if r.get("check") in ("money_decimal", "tests", "docs")]
            return {"files": [dict(f, delete=False) for f in DEMO_SOLUTION[node["kind"]]],
                    "notes": "Scripted demo change (no model configured).", "pack_refs": refs, "scripted": True}
        if _demo_applies(spec):
            return {"files": [], "notes": "Nothing to change for this task in the demo.", "pack_refs": []}
        raise RunError(NEEDS_MODEL, "needs_model")
    context = {p: working.get(p) for p in node["files"]}
    for path in list(working)[:MAX_CONTEXT_FILES]:
        context.setdefault(path, working[path])
    system, prompt = build_prompt(spec, node, context, tree, pack, failure)
    text = llm.complete_text(prompt, system=system, user_id=user_id, max_tokens=16000, effort="high")
    try:
        return _parse_files(text)
    except ValueError as exc:
        raise RunError(f"The model's answer for '{node['title']}' wasn't valid JSON") from exc


def _apply(working: dict[str, str | None], result: dict[str, Any]) -> list[str]:
    touched = []
    for f in result["files"]:
        working[f["path"]] = None if f.get("delete") else f.get("content", "")
        touched.append(f["path"])
    return touched


# -- 4. run ---------------------------------------------------------------------------

def start(store: Store, user_id: int, run_id: int) -> dict[str, Any]:
    run = _get(store, user_id, run_id)
    if run["status"] != "planned":
        raise RunError("Plan the run (and review the graph) before starting it", "conflict")
    from coworker import billing

    try:
        billing.require(store, user_id, "engineer")
    except billing.PlanError as exc:
        raise RunError(str(exc), "plan_limit") from exc
    run = _set(store, user_id, run_id, status="running", error="")
    from flask import current_app, has_app_context

    if has_app_context() and not current_app.config.get("TESTING"):
        import threading

        app = current_app._get_current_object()  # type: ignore[attr-defined]

        def target() -> None:
            with app.app_context():
                execute(store, user_id, run_id)

        threading.Thread(target=target, name=f"coworker-engineer-{run_id}", daemon=True).start()
        return run
    return execute(store, user_id, run_id)


def execute(store: Store, user_id: int, run_id: int) -> dict[str, Any]:
    run = _get(store, user_id, run_id)
    spec, nodes = run["spec"], run.get("graph") or []
    by_id = {n["id"]: n for n in nodes}
    state: dict[str, Any] = {n["id"]: {"status": "pending"} for n in nodes}
    with llm.metering() as meter:
        try:
            client, tree = _repo_context(store, user_id, spec["repo"])
            pack = knowledge_pack.current(store, user_id)
            touched = {f for n in nodes for f in n["files"]}
            original: dict[str, str | None] = {p: client.read_file(spec["repo"], p) for p in sorted(touched)}
            working: dict[str, str | None] = dict(original)
            for layer in graph.layers(nodes):
                jobs = [by_id[i] for i in layer]

                def work(node: dict[str, Any]) -> dict[str, Any]:
                    return _write_node(spec, node, dict(working), tree, pack, user_id)

                if len(jobs) > 1 and llm.available(user_id):
                    with ThreadPoolExecutor(max_workers=min(4, len(jobs))) as pool:
                        futures = [pool.submit(contextvars.copy_context().run, work, n) for n in jobs]
                        results = [f.result() for f in futures]
                else:
                    results = [work(n) for n in jobs]
                for node, result in zip(jobs, results):
                    state[node["id"]] = {"status": "done", "files": _apply(working, result), "notes": result["notes"],
                                         "pack_refs": result["pack_refs"]}
                _set(store, user_id, run_id, nodes=state)
            checks = _check_and_fix(store, user_id, run_id, spec, working, original, tree, pack, state)
        except RunError as exc:
            status = "needs_model" if exc.code == "needs_model" else "failed"
            for node_state in state.values():
                if node_state["status"] == "pending":
                    node_state["status"] = "skipped"
            store.log(user_id, "engineer", f"Run stopped: {exc}", {"run_id": run_id})
            return _set(store, user_id, run_id, status=status, error=str(exc), nodes=state,
                        cost_micros=_micros(meter))
        except Exception as exc:  # report it on the run; never crash the worker
            store.log(user_id, "engineer", f"Run failed: {exc}", {"run_id": run_id})
            return _set(store, user_id, run_id, status="failed", error=str(exc)[:1000], nodes=state,
                        cost_micros=_micros(meter))
        changes = [diffs.from_contents(p, original.get(p), working[p]) for p in sorted(working)
                   if working[p] != original.get(p)]
        result = review.review_changes(changes, pack=pack, repo=spec["repo"],
                                       suppressions=review.suppressions_for(store, user_id), user_id=user_id)
        review_row = review.save(store, user_id, result, repo=spec["repo"], source="run", run_id=run_id)
        known = {p.split("/")[0].removesuffix(".py") for p in tree} | {p.split("/")[0] for p in working}
        requirements = client.read_file(spec["repo"], "requirements.txt") or ""
        slop_report = slop.report(changes, criteria=len(spec["acceptance_criteria"]), known_modules=known,
                                  requirements=requirements,
                                  existing_code="\n".join(c or "" for c in working.values()))
        cost = _micros(meter)
    run = _set(store, user_id, run_id, nodes=state, checks=checks, slop=slop_report, review_id=review_row["id"],
               cost_micros=cost)
    if not changes:
        return _set(store, user_id, run_id, status="failed", error="The run didn't change any files.")
    return _propose_pr(store, user_id, run, working, original, result, slop_report, checks)


def _check_and_fix(store: Store, user_id: int, run_id: int, spec: dict[str, Any], working: dict[str, str | None],
                   original: dict[str, str | None], tree: list[str], pack: dict[str, Any],
                   state: dict[str, Any]) -> dict[str, Any]:
    token = ""
    if spec["repo"] != DEMO_REPO and sandbox.enabled(spec["repo"]):
        live = devtools.live_client(store, user_id, "github")
        token = str((getattr(live, "token", None) or {}).get("access_token", "")) if live else ""
    command = str(((store.get_coworker(user_id) or {}).get("settings") or {}).get("test_command") or "")
    changed = {p: c for p, c in working.items() if c != original.get(p)}
    checks = sandbox.run(spec["repo"], changed, token=token, command=command)
    attempts: list[str] = []
    while checks.get("ran") and checks.get("passed") is False and llm.available(user_id) and len(attempts) < MAX_FIX_ATTEMPTS:
        attempts.append(checks["output"][-1500:])
        fix_node: dict[str, Any] = {"id": f"fix-{len(attempts)}", "title": "Make the failing checks pass", "kind": "impl",
                    "files": sorted(changed), "criteria": []}
        result = _write_node(spec, fix_node, dict(working), tree, pack, user_id, failure=checks["output"])
        state[fix_node["id"]] = {"status": "done", "files": _apply(working, result), "notes": result["notes"],
                                 "pack_refs": result["pack_refs"]}
        _set(store, user_id, run_id, nodes=state)
        changed = {p: c for p, c in working.items() if c != original.get(p)}
        checks = sandbox.run(spec["repo"], changed, token=token, command=command)
    checks["fix_attempts"] = len(attempts)
    return checks


def _micros(meter: dict[str, Any]) -> int:
    return int(round((meter.get("cost_usd") or 0) * 1_000_000))


def min_slop(store: Store, user_id: int) -> int:
    settings = (store.get_coworker(user_id) or {}).get("settings") or {}
    try:
        return int(settings.get("engineer_min_slop_score", DEFAULT_MIN_SLOP))
    except (TypeError, ValueError):
        return DEFAULT_MIN_SLOP


def _propose_pr(store: Store, user_id: int, run: dict[str, Any], working: dict[str, str | None],
                original: dict[str, str | None], result: dict[str, Any], slop_report: dict[str, Any],
                checks: dict[str, Any]) -> dict[str, Any]:
    from coworker import executor

    spec = run["spec"]
    key = (spec.get("source") or {}).get("ref") or ""
    slug = re.sub(r"[^a-z0-9]+", "-", spec["goal"].lower()).strip("-")[:40]
    branch = f"ourogen/{slug}-{run['id']}"
    title = f"{key}: {spec['goal']}" if key and (spec.get("source") or {}).get("kind") == "jira" else spec["goal"]
    refs = sorted({r for s in (run.get("nodes") or {}).values() for r in s.get("pack_refs") or []})
    checks_line = ("✅ Tests passed" if checks.get("passed") else "❌ Tests failed" if checks.get("passed") is False
                   else f"⚪ Tests not run ({checks.get('output', '')[:120]})")
    body = "\n".join([
        f"Written by the owner's AI engineer (Ourogen) from {key or 'a chat request'}.", "",
        "## Acceptance criteria", *[f"- [x] {c}" for c in spec["acceptance_criteria"]], "",
        "## Checks", f"- {checks_line}", f"- AI review: {result['summary']}",
        f"- Slop score: {slop_report['score']}/100", "",
        "## Followed", *([f"- {r}" for r in refs] or ["- (no knowledge-pack rules cited)"]),
    ])
    risks = []
    if checks.get("passed") is False:
        risks.append({"code": "checks_failed", "message": "The tests failed."})
    if result["escalate"]:
        risks.append({"code": "review_escalation", "message": f"The reviewer wants a human look: {'; '.join(result['reasons'])}."})
    if slop_report["score"] < min_slop(store, user_id):
        risks.append({"code": "slop", "message": f"Slop score {slop_report['score']} is below your minimum of {min_slop(store, user_id)}."})
    files: list[dict[str, Any]] = [{"path": p, "delete": c is None, "content": c or ""} for p, c in sorted(working.items()) if c != original.get(p)]
    action = executor.propose(store, user_id, "github.pr",
                              {"repo": spec["repo"], "branch": branch, "title": title, "body": body, "files": files,
                               "run_id": run["id"], "diff": "".join(diffs.unified(f["path"], original.get(f["path"]),
                                                                                    working.get(f["path"])) for f in files)[:60000]},
                              title=f"Open PR: {title}", reasoning=body, extra_risks=risks)
    store.log(user_id, "engineer", f"Ready for review: {title}", {"run_id": run["id"], "action_id": action["id"]},
              action_id=action["id"])
    fresh = _get(store, user_id, run["id"])
    if fresh["status"] == "pr_opened":  # autonomy allowed it and it already ran
        return _set(store, user_id, run["id"], action_id=action["id"])
    return _set(store, user_id, run["id"], status="ready", action_id=action["id"])


def pr_opened(store: Store, user_id: int, run_id: int, result: dict[str, Any]) -> None:
    run = store.get("cw_eng_runs", run_id, user_id)
    if not run:
        return
    _set(store, user_id, run_id, status="pr_opened",
         pr={"url": result.get("url", ""), "number": result.get("external_id", ""), "branch": result.get("branch", ""),
             "demo": bool(result.get("demo"))})
    store.log(user_id, "engineer", f"Opened a pull request: {run['title']}", {"run_id": run_id, "url": result.get("url")})


def runs(store: Store, user_id: int, limit: int = 50) -> list[dict[str, Any]]:
    return store.query("SELECT * FROM cw_eng_runs WHERE user_id = %s ORDER BY id DESC LIMIT %s", (user_id, limit))


def serialize(run: dict[str, Any]) -> dict[str, Any]:
    nodes = run.get("graph") or []
    try:
        layer_list = graph.layers(nodes) if nodes else []
    except graph.GraphError:
        layer_list = []
    return {"id": run["id"], "title": run["title"], "status": run["status"], "repo": run["repo"],
            "source": run.get("source") or "", "spec": run.get("spec") or {}, "graph": nodes, "layers": layer_list,
            "nodes": run.get("nodes") or {}, "checks": run.get("checks") or {}, "slop": run.get("slop") or {},
            "pr": run.get("pr") or {}, "reviewId": run.get("review_id"), "actionId": run.get("action_id"),
            "error": run.get("error") or "", "costUsd": round((run.get("cost_micros") or 0) / 1_000_000, 4),
            "createdAt": run["created_at"], "updatedAt": run["updated_at"]}
