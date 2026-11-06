/**
 * The parts of the AI-coworker integration that don't need VS Code, so they can be tested with node:test.
 */

export interface CoworkerSettings {
  url: string;
  token: string;
}

/** `git@github.com:owner/repo.git` or `https://github.com/owner/repo(.git)` → `owner/repo`. */
export function repoFromRemote(remote: string): string {
  const m = remote.trim().match(/github\.com[:/]([\w.-]+)\/([\w.-]+?)(?:\.git)?\/?$/);
  return m ? `${m[1]}/${m[2]}` : "";
}

/** A ticket ref, a bare Jira key, or free text. */
export function workInput(input: string): { source?: string; text?: string } {
  const value = input.trim();
  if (/^(jira|notion|github):\S+$/.test(value)) return { source: value };
  if (/^[A-Z][A-Z0-9]+-\d+$/.test(value)) return { source: `jira:${value}` };
  return { text: value };
}

/** `owner/repo#12`, a GitHub PR URL, or `#12` / `12` with a default repository. */
export function parsePrRef(ref: string, defaultRepo = ""): { repo: string; number: number } | null {
  const value = ref.trim();
  const full = value.match(/^(?:https:\/\/github\.com\/)?([\w.-]+\/[\w.-]+?)(?:#|\/pull\/)(\d+)\/?$/);
  if (full) return { repo: full[1], number: Number(full[2]) };
  const short = value.match(/^#?(\d+)$/);
  return short && defaultRepo ? { repo: defaultRepo, number: Number(short[1]) } : null;
}

/** A description of selected code for the engineer: the ask, plus where the code is. */
export function selectionTask(ask: string, file: string, startLine: number, code: string): string {
  const snippet = code.length > 4000 ? `${code.slice(0, 4000)}\n…` : code;
  return `${ask.trim()}\n\nCode in ${file} (from line ${startLine}):\n\`\`\`\n${snippet}\n\`\`\``;
}

export type Severity = "high" | "medium" | "low";

export interface FindingLike {
  severity: Severity;
  path: string;
  line: number;
  title: string;
  detail: string;
  suggestion: string;
  rule?: string;
  dismissed?: boolean;
}

/** Findings grouped by file, ready to become diagnostics (lines are 0-based). */
export function findingsByFile(findings: FindingLike[]): Map<string, { line: number; severity: Severity; message: string }[]> {
  const out = new Map<string, { line: number; severity: Severity; message: string }[]>();
  for (const f of findings) {
    if (f.dismissed || !f.path) continue;
    const list = out.get(f.path) ?? [];
    list.push({
      line: Math.max(0, (f.line || 1) - 1),
      severity: f.severity,
      message: `${f.title}: ${f.detail} Suggestion: ${f.suggestion}${f.rule ? ` [${f.rule}]` : ""}`,
    });
    out.set(f.path, list);
  }
  return out;
}

export function summarizeRun(run: any): string[] {
  const lines = [`${run.title} (${run.repo}): ${run.status}`];
  for (const c of run.spec?.acceptance_criteria ?? []) lines.push(`  • ${c}`);
  (run.layers ?? []).forEach((layer: string[], i: number) => {
    const names = layer.map((id) => (run.graph ?? []).find((n: any) => n.id === id)?.title ?? id);
    lines.push(`  Step ${i + 1}: ${names.join("  ∥  ")}`);
  });
  if (run.checks && Object.keys(run.checks).length) {
    lines.push(`  Tests: ${run.checks.passed ? "passed" : run.checks.passed === false ? "failed" : "not run"}`
      + (run.slop?.score !== undefined ? ` · slop ${run.slop.score}/100` : ""));
  }
  if (run.pr?.url) lines.push(`  PR: ${run.pr.url}`);
  if (run.error) lines.push(`  ${run.error}`);
  return lines;
}

export class CoworkerApi {
  constructor(private readonly settings: CoworkerSettings, private readonly fetchImpl: typeof fetch = fetch) {}

  async call<T = any>(method: string, path: string, body?: unknown): Promise<T> {
    const res = await this.fetchImpl(`${this.settings.url.replace(/\/$/, "")}/api/coworker${path}`, {
      method,
      headers: { Authorization: `Bearer ${this.settings.token}`, "Content-Type": "application/json", "User-Agent": "anote-vscode" },
      body: body === undefined ? undefined : JSON.stringify(body),
    });
    const data = (await res.json().catch(() => ({}))) as { error?: string };
    if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);
    return data as T;
  }

  /** Create, plan and start a run; poll while it runs. `onUpdate` sees every state; `cancelled` stops polling. */
  async handOff(input: { source?: string; text?: string; repo?: string }, onUpdate: (run: any) => void = () => {},
                cancelled: () => boolean = () => false, pollMs = 3000): Promise<any> {
    let run = await this.call("POST", "/engineer/runs", input);
    onUpdate(run);
    run = await this.call("POST", `/engineer/runs/${run.id}/plan`);
    onUpdate(run);
    run = await this.call("POST", `/engineer/runs/${run.id}/start`);
    onUpdate(run);
    while (run.status === "running" && !cancelled()) {
      await new Promise((r) => setTimeout(r, pollMs));
      run = await this.call("GET", `/engineer/runs/${run.id}`);
      onUpdate(run);
    }
    return run;
  }
}
