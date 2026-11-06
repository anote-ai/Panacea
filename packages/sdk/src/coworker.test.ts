import { describe, expect, it } from "vitest";
import { AnoteError, CoworkerClient } from "./index.js";

type Call = { url: string; method: string; body?: unknown; auth?: string };

function fakeFetch(responses: Record<string, unknown[]>) {
  const calls: Call[] = [];
  const impl = (async (url: string, init: RequestInit = {}) => {
    const method = init.method ?? "GET";
    const path = new URL(url).pathname.replace("/api/coworker", "");
    calls.push({ url, method, body: init.body ? JSON.parse(String(init.body)) : undefined,
                 auth: (init.headers as Record<string, string>)?.Authorization });
    const queue = responses[`${method} ${path}`];
    const next = queue?.shift() ?? { status: 404, body: { error: "not found" } };
    const { status = 200, body = {}, text } = next as { status?: number; body?: unknown; text?: string };
    return { ok: status < 400, status, json: async () => body, text: async () => text ?? "" } as Response;
  }) as unknown as typeof fetch;
  return { impl, calls };
}

const run = (status: string, extra: object = {}) => ({ id: 7, status, checks: {}, slop: {}, pr: {}, ...extra });

describe("CoworkerClient", () => {
  it("requires an ogn_ token", () => {
    expect(() => new CoworkerClient({ token: "ant-x" })).toThrow(/ogn_/);
  });

  it("hands off a ticket: create, plan, start, and waits while running", async () => {
    const { impl, calls } = fakeFetch({
      "POST /engineer/runs": [{ body: run("spec") }],
      "POST /engineer/runs/7/plan": [{ body: run("planned") }],
      "POST /engineer/runs/7/start": [{ status: 202, body: run("running") }],
      "GET /engineer/runs/7": [{ body: run("running") }, { body: run("ready", { checks: { passed: true }, slop: { score: 100 } }) }],
    });
    const cw = new CoworkerClient({ token: "ogn_test", baseUrl: "http://localhost:5000/", fetch: impl });
    const out = await cw.engineer.handOff({ source: "jira:ACME-142", pollMs: 1 });
    expect(out.status).toBe("ready");
    expect(out.slop.score).toBe(100);
    expect(calls[0]).toMatchObject({ method: "POST", body: { source: "jira:ACME-142" }, auth: "Bearer ogn_test" });
    expect(calls[0].url).toBe("http://localhost:5000/api/coworker/engineer/runs");
  });

  it("stops after the spec when start is false, and edits it", async () => {
    const { impl, calls } = fakeFetch({
      "POST /engineer/runs": [{ body: run("spec") }],
      "PATCH /engineer/runs/7/spec": [{ body: run("spec") }],
      "PATCH /engineer/runs/7/graph": [{ body: run("planned") }],
      "GET /engineer/runs": [{ body: { runs: [run("spec")] } }],
    });
    const cw = new CoworkerClient({ token: "ogn_test", fetch: impl });
    expect((await cw.engineer.handOff({ text: "Add CSV export", start: false })).status).toBe("spec");
    await cw.engineer.editSpec(7, { constraints: ["No new dependencies"] });
    await cw.engineer.editGraph(7, [{ id: "impl", files: ["a.py"] }]);
    expect(await cw.engineer.list()).toHaveLength(1);
    expect(calls[1].body).toEqual({ constraints: ["No new dependencies"] });
    expect(calls[2].body).toEqual({ nodes: [{ id: "impl", files: ["a.py"] }] });
  });

  it("reviews, scorecard, knowledge pack, trial, and CSV", async () => {
    const { impl, calls } = fakeFetch({
      "POST /reviews": [{ status: 201, body: { id: 3, findings: [], escalate: false } }],
      "GET /reviews/3": [{ body: { id: 3 } }],
      "GET /reviews": [{ body: { reviews: [{ id: 3 }] } }],
      "GET /scorecard": [{ body: { days: 30 } }, { text: "metric,value\n" }],
      "GET /knowledge-pack": [{ body: { styleRules: [] } }],
      "GET /trial": [{ body: { trial: null } }],
    });
    const cw = new CoworkerClient({ token: "ogn_test", fetch: impl });
    expect((await cw.reviews.create("acme/api", 37)).id).toBe(3);
    expect((await cw.reviews.get(3)).id).toBe(3);
    expect(await cw.reviews.list()).toHaveLength(1);
    expect((await cw.scorecard(30)).days).toBe(30);
    expect(calls[3].url).toContain("days=30");
    expect(await cw.scorecardCsv()).toBe("metric,value\n");
    expect(await cw.knowledgePack()).toEqual({ styleRules: [] });
    expect(await cw.trial()).toEqual({ trial: null });
  });

  it("raises AnoteError with the server's message", async () => {
    const { impl } = fakeFetch({ "POST /engineer/runs/7/start": [{ status: 402, body: { error: "Out of runs", code: "plan_limit" } }],
                                 "GET /scorecard": [{ status: 401, text: "" }] });
    const cw = new CoworkerClient({ token: "ogn_test", fetch: impl });
    await expect(cw.engineer.start(7)).rejects.toMatchObject({ name: "AnoteError", status: 402, message: "Out of runs" });
    await expect(cw.scorecardCsv()).rejects.toBeInstanceOf(AnoteError);
  });
});
