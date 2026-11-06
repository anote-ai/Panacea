/**
 * CoworkerClient: hand work to your Ourogen AI coworker from code.
 *
 * Authenticates with a personal access token (`ogn_…`) from
 * Coworker → Settings → API tokens. Tokens can hand off engineering work,
 * request code reviews, and read results. Approving, sending, and billing
 * always happen in the app.
 *
 * @example
 * ```ts
 * import { CoworkerClient } from "@anote-ai/sdk";
 *
 * const cw = new CoworkerClient({ token: process.env.OUROGEN_TOKEN!, baseUrl: "https://chat.ourogen.ai" });
 * const run = await cw.engineer.handOff({ source: "jira:ACME-142" });
 * console.log(run.status, run.checks.passed, run.slop.score); // "ready", true, 100
 * ```
 */
import { AnoteError } from "./errors.js";

export interface CoworkerClientOptions {
  /** Personal access token starting with `ogn_`. */
  token: string;
  /** Your Ourogen server. Defaults to `https://chat.ourogen.ai`. */
  baseUrl?: string;
  /** Inject a fetch implementation (tests, older runtimes). */
  fetch?: typeof fetch;
}

export type RunStatus = "spec" | "planned" | "running" | "ready" | "pr_opened" | "failed" | "needs_model";

export interface Spec {
  goal: string;
  acceptance_criteria: string[];
  constraints: string[];
  repo: string;
  source: { kind: string; ref: string; title: string; url: string };
}

export interface TaskNode {
  id: string;
  title: string;
  kind: string;
  files: string[];
  depends_on: string[];
  criteria: number[];
}

export interface EngineerRun {
  id: number;
  title: string;
  status: RunStatus;
  repo: string;
  spec: Spec;
  graph: TaskNode[];
  layers: string[][];
  nodes: Record<string, { status: string; files?: string[]; notes?: string; pack_refs?: string[] }>;
  checks: { ran?: boolean; passed?: boolean | null; output?: string; fix_attempts?: number };
  slop: { score?: number; flags?: { code: string; message: string; path: string; line: number }[] };
  pr: { url?: string; number?: string; branch?: string; demo?: boolean };
  reviewId: number | null;
  actionId: number | null;
  error: string;
  costUsd: number;
}

export interface Finding {
  id: string;
  check: string;
  severity: "high" | "medium" | "low";
  path: string;
  line: number;
  title: string;
  detail: string;
  suggestion: string;
  rule: string;
  dismissed: boolean;
}

export interface Review {
  id: number;
  repo: string;
  number: number;
  findings: Finding[];
  summary: string;
  reasons: string[];
  slop: { score?: number };
  escalate: boolean;
  actionId: number | null;
}

export interface HandOffOptions {
  /** A ticket: `jira:ACME-142`, `notion:<page id>`, or `github:owner/repo#12`. */
  source?: string;
  /** Or describe the work, with acceptance criteria as bullets. */
  text?: string;
  /** `owner/name`; defaults to your coworker's default repository. */
  repo?: string;
  /** Plan and run it now (default). `false` stops after the spec so you can edit it. */
  start?: boolean;
  /** How long to wait for a background run to finish, in ms (default 10 minutes; 0 = don't wait). */
  waitMs?: number;
  /** Poll interval while waiting, in ms (default 3000). */
  pollMs?: number;
}

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

export class CoworkerClient {
  private readonly token: string;
  private readonly base: string;
  private readonly fetchImpl: typeof fetch;

  constructor(options: CoworkerClientOptions) {
    if (!options.token?.startsWith("ogn_")) throw new Error("token must be a coworker API token (ogn_…)");
    this.token = options.token;
    this.base = (options.baseUrl ?? "https://chat.ourogen.ai").replace(/\/$/, "") + "/api/coworker";
    this.fetchImpl = options.fetch ?? fetch;
  }

  private async request<T>(method: string, path: string, body?: unknown, params?: Record<string, string | number>): Promise<T> {
    let url = `${this.base}${path}`;
    if (params) url += `?${new URLSearchParams(Object.entries(params).map(([k, v]) => [k, String(v)]))}`;
    const res = await this.fetchImpl(url, {
      method,
      headers: { Authorization: `Bearer ${this.token}`, "Content-Type": "application/json", "User-Agent": "@anote-ai/sdk/1.1.0" },
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new AnoteError((data as { error?: string }).error ?? `HTTP ${res.status}`, res.status, data);
    return data as T;
  }

  /** The AI engineer: ticket → spec → task graph → code → tests → review → PR (approved in the app). */
  readonly engineer = {
    create: (opts: { source?: string; text?: string; repo?: string }) => this.request<EngineerRun>("POST", "/engineer/runs", opts),
    get: (id: number) => this.request<EngineerRun>("GET", `/engineer/runs/${id}`),
    list: async () => (await this.request<{ runs: EngineerRun[] }>("GET", "/engineer/runs")).runs,
    editSpec: (id: number, changes: Partial<Pick<Spec, "goal" | "acceptance_criteria" | "constraints" | "repo">>) =>
      this.request<EngineerRun>("PATCH", `/engineer/runs/${id}/spec`, changes),
    plan: (id: number) => this.request<EngineerRun>("POST", `/engineer/runs/${id}/plan`),
    editGraph: (id: number, nodes: Partial<TaskNode>[]) => this.request<EngineerRun>("PATCH", `/engineer/runs/${id}/graph`, { nodes }),
    start: (id: number) => this.request<EngineerRun>("POST", `/engineer/runs/${id}/start`),
    /** Wait until a run leaves `running`. */
    wait: async (id: number, waitMs = 600_000, pollMs = 3000): Promise<EngineerRun> => {
      const deadline = Date.now() + waitMs;
      let run = await this.engineer.get(id);
      while (run.status === "running" && Date.now() < deadline) {
        await sleep(pollMs);
        run = await this.engineer.get(id);
      }
      return run;
    },
    /** Create, plan and start in one call, then wait for the result. */
    handOff: async (opts: HandOffOptions): Promise<EngineerRun> => {
      let run = await this.engineer.create({ source: opts.source, text: opts.text, repo: opts.repo });
      if (opts.start === false) return run;
      run = await this.engineer.plan(run.id);
      run = await this.engineer.start(run.id);
      const waitMs = opts.waitMs ?? 600_000;
      return run.status === "running" && waitMs > 0 ? this.engineer.wait(run.id, waitMs, opts.pollMs) : run;
    },
  };

  /** The AI code reviewer. The review is posted on GitHub once approved in the app. */
  readonly reviews = {
    create: (repo: string, number: number) => this.request<Review>("POST", "/reviews", { repo, number }),
    get: (id: number) => this.request<Review>("GET", `/reviews/${id}`),
    list: async () => (await this.request<{ reviews: Review[] }>("GET", "/reviews")).reviews,
  };

  /** Work done per unit of time, over the last `days` days (default 7). */
  scorecard(days = 7): Promise<Record<string, any>> {
    return this.request("GET", "/scorecard", undefined, { days });
  }

  /** CSV export of the scorecard. */
  async scorecardCsv(days = 7): Promise<string> {
    const res = await this.fetchImpl(`${this.base}/scorecard?days=${days}&format=csv`, {
      headers: { Authorization: `Bearer ${this.token}` },
    });
    if (!res.ok) throw new AnoteError(`HTTP ${res.status}`, res.status, null);
    return res.text();
  }

  /** What your AI knows about how you work. */
  knowledgePack(): Promise<Record<string, any>> {
    return this.request("GET", "/knowledge-pack");
  }

  /** The current one-month trial, if any. */
  trial(): Promise<Record<string, any>> {
    return this.request("GET", "/trial");
  }
}
