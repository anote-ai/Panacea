"""Knowledge packs, the AI engineer, the AI code reviewer, slop checks, and the code evals."""
from __future__ import annotations

import json
from typing import Any
from unittest.mock import patch

import pytest

from coworker import executor, knowledge_pack
from coworker.connectors import devtools
from coworker.connectors.devtools_demo import REPO
from coworker.engineering import diffs, graph, review, runs, sandbox, slop
from coworker.engineering import spec as specs
from coworker.engineering.demo import DEMO_REVIEW_PATCH
from coworker.evals import code as code_evals
from coworker.store import Store


@pytest.fixture(autouse=True)
def _env(monkeypatch):
    monkeypatch.setenv("COWORKER_OFFLINE", "1")
    with patch("api_endpoints.coworker.common.owner_profile", return_value=("Natan Vidra", "natan@example.com")), \
         patch("api_endpoints.coworker.core.owner_profile", return_value=("Natan Vidra", "natan@example.com")):
        yield


@pytest.fixture
def s(tmp_path):
    store = Store(f"sqlite:///{tmp_path}/eng.db")
    store.create_coworker(1, "Natan Vidra", "natan@example.com", mode="demo")
    return store


def _model(*answers: str):
    """Pretend a model is configured and answer each call in turn."""
    queue = list(answers)

    def complete(*args: Any, **kwargs: Any) -> str:
        return queue.pop(0) if queue else "{}"

    return patch("coworker.llm.available", return_value=True), patch("coworker.llm.complete_text", side_effect=complete)


# -- knowledge packs ---------------------------------------------------------------------

def test_scrub_removes_secrets_and_other_peoples_contacts():
    text = ("token ghp_" + "a" * 36 + " key sk-ant-" + "b" * 20 + " AKIA" + "C" * 16 + " password=hunter22 "
            "mail dana@northwind.com and natan@example.com, call +1 (415) 555-0100")
    out = knowledge_pack.scrub(text, "natan@example.com")
    assert "ghp_" not in out and "sk-ant" not in out and "AKIA" not in out and "hunter22" not in out
    assert "[email]" in out and "natan@example.com" in out and "[phone]" in out


def test_demo_pack_has_skills_rules_and_playbooks_with_evidence(s):
    row = knowledge_pack.build(s, 1)
    pack = row["pack"]
    names = {sk["name"] for sk in pack["skills"]}
    assert {"Python", "Testing", "Billing & payments"} <= names
    checks = {r["check"] for r in pack["style_rules"] if r["check"]}
    assert {"tests", "money_decimal", "specific_except", "no_skipped_tests"} <= checks
    assert len(pack["playbooks"]) >= 3 and all(pb["steps"] for pb in pack["playbooks"])
    assert all(r["evidence"] for r in pack["style_rules"] if r["check"])
    assert row["sources"] == ["github", "jira", "notion"]
    assert "[rule-money_decimal]" in knowledge_pack.prompt_context(pack)


def test_pack_edits_survive_rebuilds_and_freeze_versions(s):
    knowledge_pack.build(s, 1)
    knowledge_pack.edit(s, 1, "style_rules", "remove", "rule-naming")
    knowledge_pack.edit(s, 1, "style_rules", "update", "rule-tests", {"text": "Tests first, always. ghp_" + "z" * 36})
    knowledge_pack.edit(s, 1, "style_rules", "add", values={"text": "Never float for money"})
    knowledge_pack.edit(s, 1, "playbooks", "add", values={"title": "Hotfix", "steps": ["Reproduce", "Patch", "Backport"]})
    with pytest.raises(ValueError):
        knowledge_pack.edit(s, 1, "style_rules", "update", "rule-missing", {"text": "x"})
    with pytest.raises(ValueError):
        knowledge_pack.edit(s, 1, "nope", "add")
    with pytest.raises(ValueError):
        knowledge_pack.edit(s, 1, "skills", "add", values={})
    pack = knowledge_pack.build(s, 1)["pack"]  # rebuild keeps edits
    rules = {r["id"]: r for r in pack["style_rules"]}
    assert "rule-naming" not in rules and rules["rule-tests"]["text"].startswith("Tests first") and rules["rule-tests"]["edited"]
    assert "ghp_" not in rules["rule-tests"]["text"]
    added = next(r for r in pack["style_rules"] if r["text"] == "Never float for money")
    assert added["check"] == "money_decimal"
    assert any(pb["title"] == "Hotfix" for pb in pack["playbooks"])
    v1 = knowledge_pack.freeze(s, 1)
    v2 = knowledge_pack.freeze(s, 1)
    assert (v1["version"], v2["version"]) == (1, 2) and "edits" not in v1["pack"] and "base" not in v1["pack"]
    assert [v["version"] for v in knowledge_pack.versions(s, 1)] == [2, 1]


def test_forgetting_a_source_drops_what_came_from_it(s):
    knowledge_pack.build(s, 1)
    devtools.purge(s, 1, "notion")
    knowledge_pack.forget_source(s, 1)
    row = knowledge_pack.draft(s, 1)
    assert "notion" not in row["sources"]
    assert not any(pb["title"] == "How I ship a feature" for pb in row["pack"]["playbooks"])


def test_pack_model_refinement_adds_rules_and_tolerates_bad_answers(s):
    good = json.dumps({"extra_rules": ["Log with structured fields, mail ops@acme.com"],
                       "extra_playbooks": [{"title": "Incident response", "steps": ["Page on-call", "Write a postmortem"]}]})
    available, complete = _model(good)
    with available, complete:
        pack = knowledge_pack.build(s, 1)["pack"]
    assert any(r.get("model") and "[email]" in r["text"] for r in pack["style_rules"])
    assert any(pb["title"] == "Incident response" for pb in pack["playbooks"])
    available, complete = _model("not json")
    with available, complete:
        assert knowledge_pack.build(s, 1)["pack"]["style_rules"]


def test_pack_routes(client, auth_headers):
    h = auth_headers
    assert client.get("/api/coworker/knowledge-pack", headers=h).status_code == 404
    client.post("/api/coworker", json={"mode": "demo"}, headers=h)
    pack = client.get("/api/coworker/knowledge-pack", headers=h).get_json()
    assert pack["styleRules"] and pack["playbooks"] and pack["skills"] and pack["version"] == 0
    resp = client.patch("/api/coworker/knowledge-pack", json={"section": "style_rules", "op": "remove", "id": "rule-docs"},
                        headers=h)
    assert resp.status_code == 200 and all(r["id"] != "rule-docs" for r in resp.get_json()["styleRules"])
    assert client.patch("/api/coworker/knowledge-pack", json={"section": "x", "op": "add"}, headers=h).status_code == 400
    assert client.post("/api/coworker/knowledge-pack/build", headers=h).status_code == 200
    assert client.post("/api/coworker/knowledge-pack/versions", headers=h).get_json()["version"] == 1
    assert client.get("/api/coworker/knowledge-pack/versions", headers=h).get_json()["versions"][0]["version"] == 1


# -- spec and graph --------------------------------------------------------------------------

def test_spec_heuristics():
    spec = specs.heuristic("Export invoices", "Finance needs CSV exports.\n\nAcceptance criteria:\n- Export returns CSV\n"
                                              "- Includes tax column\n\n- Don't change the PDF export")
    assert spec["goal"] == "Export invoices" and spec["acceptance_criteria"][:2] == ["Export returns CSV", "Includes tax column"]
    assert spec["constraints"] == ["Don't change the PDF export"]
    prose = specs.heuristic("", "Add a dark mode toggle. It should remember the choice. Keep the default light.")
    assert prose["acceptance_criteria"] == ["Add a dark mode toggle.", "It should remember the choice."]
    assert prose["constraints"] == ["Keep the default light."]
    with pytest.raises(ValueError):
        specs.parse_source("trello:abc")
    with pytest.raises(ValueError):
        specs.validate({"goal": "", "acceptance_criteria": ["x"], "repo": "a/b"})
    with pytest.raises(ValueError):
        specs.validate({"goal": "g", "acceptance_criteria": [], "repo": "a/b"})
    with pytest.raises(ValueError):
        specs.validate({"goal": "g", "acceptance_criteria": ["c"], "repo": "nope"})


def test_spec_sources(s):
    jira = specs.make(s, 1, source="jira:acme-142")
    assert jira["source"]["ref"] == "ACME-142" and len(jira["acceptance_criteria"]) == 4 and jira["repo"] == REPO
    page = specs.fetch_source(s, 1, "notion:how-i-ship")
    assert page["title"] == "How I ship a feature"
    with pytest.raises(ValueError):
        specs.fetch_source(s, 1, "github:a/b")
    with pytest.raises(ValueError):
        specs.make(s, 1, text="  ")
    chat = specs.make(s, 1, text="Add CSV export\n- returns a CSV file", repo="acme/api")
    assert chat["repo"] == "acme/api" and chat["source"]["kind"] == "chat"
    s.update_coworker(1, settings={"default_repo": "acme/web"})
    assert specs.default_repo(s, 1) == "acme/web"
    available, complete = _model(json.dumps({"goal": "Better goal", "acceptance_criteria": ["A"], "constraints": []}))
    with available, complete:
        assert specs.make(s, 1, text="Do a thing\n- it works")["goal"] == "Better goal"


def test_graph_layers_and_validation():
    spec = {"goal": "Annual quote endpoint", "acceptance_criteria": ["The API returns an annual quote", "Documented in README"]}
    nodes = graph.heuristic(spec, ["app/pricing.py", "app/api.py", "tests/test_pricing.py", "README.md"],
                            {"app/pricing.py": "def monthly_quote(): ...", "app/api.py": "route quote"})
    assert [n["id"] for n in nodes] == ["interface", "impl", "test", "docs"]
    assert graph.layers(nodes) == [["interface"], ["impl"], ["docs", "test"]]
    new_file = graph.heuristic({"goal": "Webhook retries", "acceptance_criteria": ["retries 3 times"]}, ["src/index.ts"])
    assert new_file[0]["files"] == ["webhook_retries.py"]
    assert graph._test_path_for("src/retry.ts", [], "x") == "src/retry.test.ts"
    for bad, message in [([], "at least one"), ([{"id": "a"}, {"id": "a"}], "unique"),
                         ([{"id": "a", "depends_on": ["b"]}], "unknown"),
                         ([{"id": "a", "depends_on": ["b"]}, {"id": "b", "depends_on": ["a"]}], "cycle"),
                         ([{"id": "a", "files": ["../etc/passwd"]}], "inside"),
                         ([{"id": str(i)} for i in range(21)], "20")]:
        with pytest.raises(graph.GraphError, match=message):
            graph.validate(bad)
    clean = graph.validate([{"id": "Impl Step", "kind": "weird", "files": ["/a.py"], "criteria": [0, "x"]}])
    assert clean[0] == {"id": "impl-step", "title": "impl-step", "kind": "impl", "files": ["a.py"], "depends_on": [],
                        "criteria": [0]}


def test_graph_plan_uses_the_model_when_valid():
    spec = {"goal": "g", "acceptance_criteria": ["c"]}
    good = json.dumps({"nodes": [{"id": "only", "title": "Do it", "kind": "impl", "files": ["a.py"]}]})
    available, complete = _model(good)
    with available, complete:
        assert [n["id"] for n in graph.plan(spec, ["a.py"], user_id=1)] == ["only"]
    available, complete = _model(json.dumps({"nodes": [{"id": "a", "depends_on": ["a"]}]}))
    with available, complete:
        assert graph.plan(spec, ["a.py"], user_id=1)[0]["id"] == "impl"


# -- the engineer -------------------------------------------------------------------------------

def test_demo_run_end_to_end_then_approve_opens_the_pr(s):
    run = runs.create(s, 1, source="jira:ACME-142")
    assert run["status"] == "spec"
    with pytest.raises(runs.RunError):
        runs.start(s, 1, run["id"])
    run = runs.plan(s, 1, run["id"])
    assert run["status"] == "planned" and run["graph"][0]["files"] == ["app/pricing.py"]
    run = runs.start(s, 1, run["id"])
    assert run["status"] == "ready", run["error"]
    assert run["checks"]["passed"] is True and run["slop"]["score"] >= 90
    assert all(state["status"] == "done" for state in run["nodes"].values())
    assert any(state["pack_refs"] for state in run["nodes"].values())
    action = s.get("cw_actions", run["action_id"], 1)
    assert action["type"] == "github.pr" and action["status"] == "proposed"
    assert action["payload"]["title"].startswith("ACME-142:") and "app/pricing.py" in action["payload"]["diff"]
    executor.approve(s, 1, action["id"])
    opened = s.get("cw_eng_runs", run["id"], 1)
    assert opened["status"] == "pr_opened" and opened["pr"]["demo"] and opened["pr"]["url"]
    with pytest.raises(runs.RunError):
        runs.update_spec(s, 1, run["id"], {"goal": "x"})


def test_run_outside_the_demo_needs_a_model(s):
    run = runs.create(s, 1, text="Add CSV export\n- returns a CSV", repo=REPO)
    runs.plan(s, 1, run["id"])
    out = runs.start(s, 1, run["id"])
    assert out["status"] == "needs_model" and "API key" in out["error"]
    assert all(st["status"] == "skipped" for st in out["nodes"].values())


def test_run_with_a_model_retries_failing_checks(s):
    knowledge_pack.build(s, 1)  # offline, so the model answers below go to the run
    run = runs.create(s, 1, text="Add a refund helper\n- refund(amount) returns the amount as Decimal", repo=REPO)
    run = runs.plan(s, 1, run["id"])
    run = runs.update_graph(s, 1, run["id"], [{"id": "impl", "title": "Write refund", "kind": "impl",
                                                  "files": ["app/refunds.py"]},
                                                 {"id": "test", "title": "Test it", "kind": "test",
                                                  "files": ["tests/test_refunds.py"], "depends_on": ["impl"]}])
    broken = json.dumps({"files": [{"path": "app/refunds.py", "content": "def refund(amount):\n    return amount + 1\n"}],
                         "notes": "first try", "pack_refs": ["rule-money_decimal"]})
    test = json.dumps({"files": [{"path": "tests/test_refunds.py", "content":
                                  "from decimal import Decimal\n\nfrom app.refunds import refund\n\n\n"
                                  "def test_refund():\n    assert refund(Decimal('5')) == Decimal('5')\n"}],
                       "notes": "", "pack_refs": ["rule-tests"]})
    fixed = json.dumps({"files": [{"path": "app/refunds.py", "content": "def refund(amount):\n    return amount\n"}],
                        "notes": "fixed", "pack_refs": []})
    review_answer = json.dumps({"findings": [], "unsure": False})
    available, complete = _model(broken, test, fixed, review_answer)
    with available, complete:
        out = runs.start(s, 1, run["id"])
    assert out["status"] == "ready", out["error"]
    assert out["checks"]["passed"] is True and out["checks"]["fix_attempts"] == 1 and "fix-1" in out["nodes"]


def test_run_failures_are_reported(s):
    knowledge_pack.build(s, 1)
    run = runs.create(s, 1, text="Add a thing\n- it works", repo=REPO)
    runs.plan(s, 1, run["id"])
    available, complete = _model("no json here")
    with available, complete:
        out = runs.start(s, 1, run["id"])
    assert out["status"] == "failed" and "valid JSON" in out["error"]
    run = runs.create(s, 1, text="Add a thing\n- it works", repo=REPO)
    runs.plan(s, 1, run["id"])
    available, complete = _model(json.dumps({"files": [], "notes": ""}), json.dumps({"files": []}), json.dumps({"files": []}))
    with available, complete:
        out = runs.start(s, 1, run["id"])
    assert out["status"] == "failed" and "didn't change" in out["error"]
    run = runs.create(s, 1, text="Add a thing\n- it works", repo=REPO)
    runs.plan(s, 1, run["id"])
    with patch("coworker.engineering.runs.knowledge_pack.current", side_effect=RuntimeError("db down")):
        out = runs.start(s, 1, run["id"])
    assert out["status"] == "failed" and "db down" in out["error"]
    with pytest.raises(runs.RunError):
        runs.update_graph(s, 1, run["id"], [])
    with pytest.raises(runs.RunError):
        runs.plan(s, 1, run["id"])
    with pytest.raises(runs.RunError):
        runs.create(s, 1, text="")


def test_risky_runs_wait_for_a_human(s):
    s.update_coworker(1, autonomy={"github.pr": "silent"}, settings={"engineer_min_slop_score": 101})
    run = runs.create(s, 1, source="jira:ACME-142")
    runs.plan(s, 1, run["id"])
    out = runs.start(s, 1, run["id"])
    action = s.get("cw_actions", out["action_id"], 1)
    assert action["status"] == "proposed" and any(r["code"] == "slop" for r in action["risk"])
    s.update_coworker(1, settings={"engineer_min_slop_score": 0})
    run = runs.create(s, 1, source="jira:ACME-142")
    runs.plan(s, 1, run["id"])
    out = runs.start(s, 1, run["id"])
    assert out["status"] == "pr_opened"  # silent autonomy, nothing flagged: it opened right away
    s.update_coworker(1, settings={"engineer_min_slop_score": "x"})
    assert runs.min_slop(s, 1) == runs.DEFAULT_MIN_SLOP


def test_prompt_includes_criteria_pack_and_failure():
    spec = {"goal": "g", "acceptance_criteria": ["first", "second"], "constraints": ["no new deps"]}
    node = {"id": "impl", "title": "t", "kind": "impl", "files": ["a.py"], "criteria": [1]}
    system, prompt = runs.build_prompt(spec, node, {"a.py": "x = 1", "b.py": None}, ["a.py"],
                                       {"style_rules": [{"id": "rule-x", "text": "Rule"}]}, failure="boom")
    assert "second" in prompt and "first" not in prompt and "[rule-x]" in prompt and "boom" in prompt
    assert "(new file)" in prompt and "no new deps" in prompt and "Never skip" in system
    parsed = runs._parse_files('x {"files": [{"path": "../evil"}, {"path": "/ok.py", "content": "1"}], "pack_refs": ["r"]} y')
    assert [f["path"] for f in parsed["files"]] == ["ok.py"]


def test_engineer_routes(client, auth_headers):
    h = auth_headers
    assert client.post("/api/coworker/engineer/runs", json={"source": "jira:ACME-142"}, headers=h).status_code == 404
    client.post("/api/coworker", json={"mode": "demo"}, headers=h)
    assert client.post("/api/coworker/engineer/runs", json={"source": "bad"}, headers=h).status_code == 400
    run = client.post("/api/coworker/engineer/runs", json={"source": "jira:ACME-142"}, headers=h).get_json()
    rid = run["id"]
    assert run["status"] == "spec" and run["spec"]["acceptance_criteria"]
    edited = client.patch(f"/api/coworker/engineer/runs/{rid}/spec",
                          json={"constraints": ["No new dependencies"]}, headers=h).get_json()
    assert edited["spec"]["constraints"] == ["No new dependencies"]
    planned = client.post(f"/api/coworker/engineer/runs/{rid}/plan", headers=h).get_json()
    assert planned["status"] == "planned" and planned["layers"][0] == ["impl"]
    assert client.patch(f"/api/coworker/engineer/runs/{rid}/graph", json={"nodes": "x"}, headers=h).status_code == 400
    assert client.patch(f"/api/coworker/engineer/runs/{rid}/graph", json={"nodes": [{"id": "a", "depends_on": ["z"]}]},
                        headers=h).status_code == 400
    done = client.post(f"/api/coworker/engineer/runs/{rid}/start", headers=h)
    assert done.status_code == 202 and done.get_json()["status"] == "ready"
    assert client.post(f"/api/coworker/engineer/runs/{rid}/start", headers=h).status_code == 409
    assert client.post(f"/api/coworker/engineer/runs/{rid}/plan", headers=h).status_code == 409
    assert client.get(f"/api/coworker/engineer/runs/{rid}", headers=h).get_json()["reviewId"]
    assert client.get("/api/coworker/engineer/runs/999", headers=h).status_code == 404
    assert client.patch("/api/coworker/engineer/runs/999/spec", json={}, headers=h).status_code == 404
    assert len(client.get("/api/coworker/engineer/runs", headers=h).get_json()["runs"]) == 1
    client.patch("/api/coworker", json={"settings": {"default_repo": "acme/api", "engineer_min_slop_score": 80}}, headers=h)
    settings = client.get("/api/coworker", headers=h).get_json()["coworker"]["settings"]
    assert settings["default_repo"] == "acme/api" and settings["engineer_min_slop_score"] == 80


# -- the reviewer and slop -------------------------------------------------------------------

def test_reviewer_findings_with_and_without_the_pack(s):
    pack = knowledge_pack.current(s, 1)
    changes = diffs.from_github_files(DEMO_REVIEW_PATCH)
    result = review.review_changes(changes, pack=pack, use_model=False)
    checks = [f["check"] for f in result["findings"]]
    assert {"money_decimal", "no_skipped_tests", "specific_except", "early_return"} <= set(checks)
    assert result["findings"][0]["severity"] == "high" and result["escalate"]
    assert all(f["rule"] for f in result["findings"])
    bare = review.review_changes(changes, pack={}, use_model=False)
    assert "money_decimal" not in {f["check"] for f in bare["findings"]}
    sensitive = review.review_changes([diffs.from_contents("app/auth/login.py", "", "def login(user_name):\n    return 1\n"),
                                       diffs.from_contents("tests/test_login.py", "", "def test_login():\n    assert 1\n")],
                                      pack=pack, use_model=False)
    assert sensitive["escalate"] and "sensitive" in sensitive["reasons"][0]
    big = review.review_changes([diffs.from_contents(f"app/m{i}.py", "", "X = 1\n") for i in range(13)], pack=pack,
                                use_model=False)
    assert "small_pr" in {f["check"] for f in big["findings"]}
    named = review.review_changes([diffs.from_contents("app/q.py", "", "def quote(n, seat_count):\n    return n\n")],
                                  pack=pack, use_model=False)
    assert "naming" in {f["check"] for f in named["findings"]}
    assert review.review_changes([], pack=pack, use_model=False)["summary"] == "No problems found."


def test_reviewer_model_pass_merges_findings_and_flags_uncertainty(s):
    changes = diffs.from_github_files(DEMO_REVIEW_PATCH)
    answer = json.dumps({"findings": [{"path": "app/refunds.py", "line": 13, "severity": "urgent", "title": "Off by one",
                                       "detail": "d", "suggestion": "s", "rule": ""}], "unsure": True})
    available, complete = _model(answer)
    with available, complete:
        result = review.review_changes(changes, pack={}, user_id=1)
    model = [f for f in result["findings"] if f["check"] == "model"]
    assert model and model[0]["severity"] == "medium" and "the reviewer wasn't sure" in result["reasons"]
    available, complete = _model("garbage")
    with available, complete:
        assert "the reviewer wasn't sure" in review.review_changes(changes, pack={}, user_id=1)["reasons"]


def test_review_pull_request_proposes_inline_review_and_learns_from_dismissals(s):
    row = review.review_pull_request(s, 1, REPO, 37)
    action = s.get("cw_actions", row["action_id"], 1)
    assert action["type"] == "github.review" and action["payload"]["event"] == "REQUEST_CHANGES"
    assert action["payload"]["comments"] and any(r["code"] == "review_escalation" for r in action["risk"])
    finding = next(f for f in row["findings"] if f["check"] == "early_return")
    after = review.dismiss(s, 1, row["id"], finding["id"], scope="repo")
    assert next(f for f in after["findings"] if f["id"] == finding["id"])["dismissed"]
    again = review.review_pull_request(s, 1, REPO, 37)
    assert "early_return" not in {f["check"] for f in again["findings"]}
    review.dismiss(s, 1, row["id"], finding["id"], scope="repo")  # same rule twice is stored once
    assert len(review.suppressions_for(s, 1)) == 1
    with pytest.raises(LookupError):
        review.dismiss(s, 1, 999, "x")
    with pytest.raises(LookupError):
        review.dismiss(s, 1, row["id"], "missing")


def test_review_routes(client, auth_headers):
    h = auth_headers
    client.post("/api/coworker", json={"mode": "demo"}, headers=h)
    assert client.post("/api/coworker/reviews", json={"repo": "x"}, headers=h).status_code == 400
    created = client.post("/api/coworker/reviews", json={"repo": REPO, "number": 37}, headers=h)
    assert created.status_code == 201
    body = created.get_json()
    assert body["escalate"] and body["findings"] and body["slop"]["score"] < 100
    rid, fid = body["id"], body["findings"][0]["id"]
    assert client.get(f"/api/coworker/reviews/{rid}", headers=h).status_code == 200
    assert client.get("/api/coworker/reviews/999", headers=h).status_code == 404
    assert client.post(f"/api/coworker/reviews/{rid}/findings/{fid}/dismiss", json={"scope": "bad"}, headers=h).status_code == 400
    assert client.post(f"/api/coworker/reviews/{rid}/findings/nope/dismiss", json={}, headers=h).status_code == 404
    out = client.post(f"/api/coworker/reviews/{rid}/findings/{fid}/dismiss", json={"scope": "everywhere"}, headers=h)
    assert out.status_code == 200
    assert len(client.get("/api/coworker/reviews", headers=h).get_json()["reviews"]) == 1
    client.post("/api/coworker", json={"mode": "live"}, headers=h)


def test_slop_report_flags():
    report = slop.report([diffs.from_contents("tests/test_a.py", "def test_a():\n    assert 1\n    assert 2\n",
                                              "import pytest\n\n\n@pytest.mark.skip\ndef test_a():\n    pass\n"),
                          diffs.from_contents("app/x.py", "", "import fastmoneyz\n\nprint('debug')\n"
                                              "try:\n    pass\nexcept:\n    pass\n" + "VALUE = compute_something_long(1)\n" * 3)],
                         criteria=0)
    codes = {f["code"] for f in report["flags"]}
    assert {"skipped_test", "weakened_test", "unknown_import", "debug_left", "bare_except", "duplicated_block"} <= codes
    assert report["score"] < 50 and report["files"] == 2
    clean = slop.report([diffs.from_contents("app/x.py", "", "import requests\n"), ], requirements="requests==2.0\n")
    assert clean["score"] == 100


def test_diffs_helpers():
    change = diffs.from_patch("a.py", "@@ -1,2 +1,3 @@\n x\n-y\n+z\n+w\n\\ No newline at end of file\n")
    assert change["added"] == [(2, "z"), (3, "w")] and change["removed"] == ["y"]
    assert diffs.from_contents("a.py", None, "x\n")["status"] == "added"
    assert diffs.from_contents("a.py", "x\n", None)["status"] == "removed"
    assert diffs.is_test("src/__tests__/a.ts") and diffs.is_test("pkg/a_test.go") and not diffs.is_test("app/x.py")
    assert diffs.size([change]) == 3


def test_sandbox(monkeypatch):
    monkeypatch.delenv("COWORKER_SANDBOX", raising=False)
    off = sandbox.run("acme/real", {"a.py": "x"})
    assert off["ran"] is False and "COWORKER_SANDBOX" in off["output"]
    assert sandbox.detect_command(["package.json"]) == ["npm", "test", "--silent"]
    assert sandbox.detect_command(["go.mod"])[0] == "go" and sandbox.detect_command(["Cargo.toml"])[0] == "cargo"
    assert sandbox.detect_command(["README"]) == [] and sandbox.detect_command([], "make test") == ["make", "test"]
    assert sandbox.run(REPO, {"../escape.py": "x"})["output"].startswith("Sandbox error")
    failing = sandbox.run(REPO, {"tests/test_bad.py": "def test_bad():\n    assert False\n"})
    assert failing["ran"] and failing["passed"] is False
    assert sandbox.run(REPO, {}, command="definitely-not-a-binary")["output"].endswith("isn't installed here.")
    monkeypatch.setenv("COWORKER_SANDBOX", "1")
    import subprocess

    with patch("coworker.engineering.sandbox.subprocess.run",
               side_effect=subprocess.CalledProcessError(128, ["git", "clone", "https://x-access-token:SECRET@github.com"])):
        cloned = sandbox.run("acme/real", {"a.py": "x"}, token="SECRET")
    assert "SECRET" not in cloned["output"] and cloned["output"] == "Couldn't clone acme/real."
    with patch("coworker.engineering.sandbox.subprocess.run", side_effect=subprocess.TimeoutExpired(["git", "SECRET"], 1)):
        assert "SECRET" not in sandbox.run("acme/real", {}, token="SECRET")["output"]


# -- the code evals ----------------------------------------------------------------------------

def test_code_eval_suites_pass(s):
    code_evals.seed(s)
    for name, fn in code_evals.SUITES.items():
        result = fn(s)
        assert result["score"] >= code_evals.THRESHOLDS[name], (name, result["misses"])
