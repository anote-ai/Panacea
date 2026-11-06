import { test } from "node:test";
import * as assert from "node:assert/strict";
import { CoworkerApi, findingsByFile, parsePrRef, repoFromRemote, selectionTask, summarizeRun, workInput } from "./coworkerCore";

test("repo from a git remote", () => {
  assert.equal(repoFromRemote("git@github.com:acme/api.git"), "acme/api");
  assert.equal(repoFromRemote("https://github.com/acme/api"), "acme/api");
  assert.equal(repoFromRemote("https://x-access-token:t@github.com/acme/api.git\n"), "acme/api");
  assert.equal(repoFromRemote("https://gitlab.com/acme/api.git"), "");
});

test("work input and PR refs", () => {
  assert.deepEqual(workInput("ACME-142"), { source: "jira:ACME-142" });
  assert.deepEqual(workInput("notion:abc"), { source: "notion:abc" });
  assert.deepEqual(workInput(" add csv export "), { text: "add csv export" });
  assert.deepEqual(parsePrRef("acme/api#37"), { repo: "acme/api", number: 37 });
  assert.deepEqual(parsePrRef("https://github.com/acme/api/pull/9"), { repo: "acme/api", number: 9 });
  assert.deepEqual(parsePrRef("#5", "acme/api"), { repo: "acme/api", number: 5 });
  assert.equal(parsePrRef("5"), null);
});

test("selection task and findings", () => {
  const task = selectionTask("Make this handle refunds", "app/x.py", 10, "def f():\n    pass");
  assert.match(task, /Make this handle refunds\n\nCode in app\/x.py \(from line 10\)/);
  assert.ok(selectionTask("x", "a", 1, "y".repeat(5000)).endsWith("…\n```"));
  const grouped = findingsByFile([
    { severity: "high", path: "a.py", line: 3, title: "Money as float", detail: "d.", suggestion: "s", rule: "rule-money" },
    { severity: "low", path: "a.py", line: 0, title: "t", detail: "d.", suggestion: "s" },
    { severity: "low", path: "", line: 0, title: "PR-wide", detail: "d", suggestion: "s" },
    { severity: "low", path: "b.py", line: 1, title: "gone", detail: "d", suggestion: "s", dismissed: true },
  ]);
  assert.deepEqual([...grouped.keys()], ["a.py"]);
  assert.equal(grouped.get("a.py")![0].line, 2);
  assert.match(grouped.get("a.py")![0].message, /\[rule-money\]$/);
  assert.equal(grouped.get("a.py")![1].line, 0);
});

test("summarize a run", () => {
  const lines = summarizeRun({ title: "T", repo: "a/b", status: "ready", spec: { acceptance_criteria: ["c"] },
    layers: [["impl"], ["test", "docs"]], graph: [{ id: "impl", title: "Implement" }],
    checks: { passed: true }, slop: { score: 100 }, pr: { url: "u" }, error: "" });
  assert.deepEqual(lines, ["T (a/b): ready", "  • c", "  Step 1: Implement", "  Step 2: test  ∥  docs",
    "  Tests: passed · slop 100/100", "  PR: u"]);
});

test("hand off polls until done, and surfaces server errors", async () => {
  const seen: string[] = [];
  const replies: Record<string, any[]> = {
    "POST /engineer/runs": [{ id: 1, status: "spec" }], "POST /engineer/runs/1/plan": [{ id: 1, status: "planned" }],
    "POST /engineer/runs/1/start": [{ id: 1, status: "running" }], "GET /engineer/runs/1": [{ id: 1, status: "ready" }],
  };
  const fake = (async (url: string, init: any) => {
    const key = `${init.method} ${url.replace("http://h/api/coworker", "")}`;
    seen.push(key);
    const body = replies[key]?.shift();
    return body ? { ok: true, status: 200, json: async () => body } : { ok: false, status: 403, json: async () => ({ error: "nope" }) };
  }) as unknown as typeof fetch;
  const api = new CoworkerApi({ url: "http://h/", token: "ogn_x" }, fake);
  const states: string[] = [];
  const run = await api.handOff({ source: "jira:ACME-142" }, (r) => states.push(r.status), () => false, 1);
  assert.equal(run.status, "ready");
  assert.deepEqual(states, ["spec", "planned", "running", "ready"]);
  await assert.rejects(api.call("POST", "/actions/1/approve"), /nope/);
});
