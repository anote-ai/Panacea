import { describe, expect, it } from "vitest";
import * as fs from "fs";
import * as os from "os";
import * as path from "path";
import { CoworkerApi, formatReview, formatRun, loadSettings, parsePrRef, saveSettings, settingsPath, workInput } from "../commands/coworker.js";

describe("anote coworker", () => {
  it("parses PR references", () => {
    expect(parsePrRef("acme/api#37")).toEqual({ repo: "acme/api", number: 37 });
    expect(parsePrRef("https://github.com/acme/api/pull/12/")).toEqual({ repo: "acme/api", number: 12 });
    expect(parsePrRef("acme#3")).toBeNull();
  });

  it("turns arguments into a ticket source or text", () => {
    expect(workInput(["jira:ACME-142"])).toEqual({ source: "jira:ACME-142" });
    expect(workInput(["ACME-142"])).toEqual({ source: "jira:ACME-142" });
    expect(workInput(["github:acme/api#4"])).toEqual({ source: "github:acme/api#4" });
    expect(workInput(["Add", "CSV", "export"])).toEqual({ text: "Add CSV export" });
  });

  it("saves the token privately and prefers the environment", () => {
    const home = fs.mkdtempSync(path.join(os.tmpdir(), "cw-"));
    expect(loadSettings({}, home)).toBeNull();
    saveSettings({ token: "ogn_saved", url: "https://x.example" }, home);
    expect((fs.statSync(settingsPath(home)).mode & 0o777).toString(8)).toBe("600");
    expect(loadSettings({}, home)).toEqual({ token: "ogn_saved", url: "https://x.example" });
    expect(loadSettings({ OUROGEN_TOKEN: "ogn_env", OUROGEN_URL: "http://localhost:5000/" }, home))
      .toEqual({ token: "ogn_env", url: "http://localhost:5000" });
  });

  it("hands off, plans, starts, and polls until done", async () => {
    const seen: string[] = [];
    const replies: Record<string, any[]> = {
      "POST /engineer/runs": [{ id: 7, status: "spec", title: "t" }],
      "POST /engineer/runs/7/plan": [{ id: 7, status: "planned", title: "t" }],
      "POST /engineer/runs/7/start": [{ id: 7, status: "running", title: "t" }],
      "GET /engineer/runs/7": [{ id: 7, status: "ready", title: "t" }],
      "GET /scorecard?days=7&format=csv": ["metric,value\n"],
    };
    const fake = (async (url: string, init: RequestInit = {}) => {
      const key = `${init.method} ${url.replace("http://h/api/coworker", "")}`;
      seen.push(key);
      const body = replies[key]?.shift();
      if (body === undefined) return { ok: false, status: 403, json: async () => ({ error: "API tokens can't do this" }) };
      return { ok: true, status: 200, json: async () => body, text: async () => body };
    }) as unknown as typeof fetch;
    const client = new CoworkerApi({ url: "http://h", token: "ogn_x" }, fake);
    const run = await client.handOff({ source: "jira:ACME-142" }, true, 1);
    expect(run.status).toBe("ready");
    expect(seen).toEqual(["POST /engineer/runs", "POST /engineer/runs/7/plan", "POST /engineer/runs/7/start", "GET /engineer/runs/7"]);
    expect(await client.call("GET", "/scorecard?days=7&format=csv")).toBe("metric,value\n");
    await expect(client.call("POST", "/actions/1/approve")).rejects.toThrow("API tokens can't do this");
    const planned = await new CoworkerApi({ url: "http://h", token: "ogn_x" }, (async (url: string, init: RequestInit = {}) =>
      ({ ok: true, status: 200, json: async () => ({ id: 1, status: init.method === "POST" && url.endsWith("/plan") ? "planned" : "spec" }) })) as unknown as typeof fetch)
      .handOff({ text: "x" }, false);
    expect(planned.status).toBe("planned");
  });

  it("formats runs and reviews", () => {
    const text = formatRun({ title: "Annual billing", repo: "acme/api", status: "ready", spec: { acceptance_criteria: ["a"] },
      layers: [["impl"], ["test", "docs"]], graph: [{ id: "impl", title: "Implement" }], nodes: { impl: { status: "done" } },
      checks: { passed: true }, slop: { score: 100 }, pr: { url: "https://x/pull/1" }, error: "" });
    expect(text).toContain("Implement");
    expect(text).toContain("slop 100/100");
    expect(text).toContain("waiting for your approval");
    expect(formatReview({ repo: "a/b", number: 1, summary: "1 finding", escalate: true, reasons: ["high"],
      findings: [{ severity: "high", title: "Money as float", path: "a.py", line: 3 }] })).toContain("Money as float");
  });
});
