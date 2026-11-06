/**
 * `anote coworker` — hand work to your Ourogen AI coworker from the terminal.
 *
 *   anote coworker login --token ogn_… [--url https://chat.ourogen.ai]
 *   anote coworker engineer jira:ACME-142            # spec → plan → code → tests → review → PR (approve in the app)
 *   anote coworker engineer "Add CSV export" --repo acme/api --plan-only
 *   anote coworker review acme/api#37
 *   anote coworker runs
 *   anote coworker scorecard --days 30 [--csv]
 *
 * Uses a personal access token (Coworker → Settings → API tokens), or the
 * OUROGEN_TOKEN / OUROGEN_URL environment variables. Tokens can't approve
 * anything: pull requests and reviews wait for you in the app.
 */
import { Command } from "commander";
import chalk from "chalk";
import * as fs from "fs";
import * as os from "os";
import * as path from "path";

export interface CoworkerSettings {
  url: string;
  token: string;
}

const DEFAULT_URL = "https://chat.ourogen.ai";

export function settingsPath(home: string = os.homedir()): string {
  return path.join(home, ".anote", "coworker.json");
}

export function loadSettings(env: NodeJS.ProcessEnv = process.env, home: string = os.homedir()): CoworkerSettings | null {
  let saved: Partial<CoworkerSettings> = {};
  try {
    saved = JSON.parse(fs.readFileSync(settingsPath(home), "utf-8"));
  } catch {
    /* not logged in yet */
  }
  const token = env.OUROGEN_TOKEN || saved.token || "";
  if (!token) return null;
  return { token, url: (env.OUROGEN_URL || saved.url || DEFAULT_URL).replace(/\/$/, "") };
}

export function saveSettings(settings: CoworkerSettings, home: string = os.homedir()): string {
  const file = settingsPath(home);
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, JSON.stringify(settings, null, 2), { mode: 0o600 });
  return file;
}

/** `owner/repo#12` or `https://github.com/owner/repo/pull/12` → { repo, number }. */
export function parsePrRef(ref: string): { repo: string; number: number } | null {
  const m = ref.trim().match(/^(?:https:\/\/github\.com\/)?([\w.-]+\/[\w.-]+?)(?:#|\/pull\/)(\d+)\/?$/);
  return m ? { repo: m[1], number: Number(m[2]) } : null;
}

/** A ticket ref (`jira:KEY-1`, `notion:…`, `github:owner/repo#1`), a bare Jira key, or free text. */
export function workInput(words: string[]): { source?: string; text?: string } {
  const joined = words.join(" ").trim();
  if (/^(jira|notion|github):\S+$/.test(joined)) return { source: joined };
  if (/^[A-Z][A-Z0-9]+-\d+$/.test(joined)) return { source: `jira:${joined}` };
  return { text: joined };
}

export class CoworkerApi {
  constructor(private readonly settings: CoworkerSettings, private readonly fetchImpl: typeof fetch = fetch) {}

  async call<T = any>(method: string, p: string, body?: unknown): Promise<T> {
    const res = await this.fetchImpl(`${this.settings.url}/api/coworker${p}`, {
      method,
      headers: { Authorization: `Bearer ${this.settings.token}`, "Content-Type": "application/json", "User-Agent": "anote-cli" },
      body: body === undefined ? undefined : JSON.stringify(body),
    });
    if (p.includes("format=csv") && res.ok) return (await res.text()) as T;
    const data = (await res.json().catch(() => ({}))) as { error?: string };
    if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);
    return data as T;
  }

  async handOff(input: { source?: string; text?: string; repo?: string }, start: boolean, pollMs = 3000,
                onUpdate: (run: any) => void = () => {}): Promise<any> {
    let run = await this.call("POST", "/engineer/runs", input);
    onUpdate(run);
    run = await this.call("POST", `/engineer/runs/${run.id}/plan`);
    onUpdate(run);
    if (!start) return run;
    run = await this.call("POST", `/engineer/runs/${run.id}/start`);
    while (run.status === "running") {
      await new Promise((r) => setTimeout(r, pollMs));
      run = await this.call("GET", `/engineer/runs/${run.id}`);
    }
    return run;
  }
}

export function formatRun(run: any): string {
  const lines = [chalk.bold(`\n  ${run.title}`) + chalk.gray(`  ${run.repo} · ${run.status}`)];
  const criteria: string[] = run.spec?.acceptance_criteria ?? [];
  if (criteria.length) lines.push(chalk.dim("  Acceptance criteria"), ...criteria.map((c) => `   • ${c}`));
  (run.layers ?? []).forEach((layer: string[], i: number) => {
    const tasks = layer.map((id) => {
      const node = (run.graph ?? []).find((n: any) => n.id === id);
      const state = run.nodes?.[id]?.status ?? "pending";
      return `${node?.title ?? id} ${chalk.gray(`[${state}]`)}`;
    });
    lines.push(`  ${chalk.dim(`Step ${i + 1}`)}  ${tasks.join(chalk.gray("  ∥  "))}`);
  });
  if (run.checks && Object.keys(run.checks).length) {
    const verdict = run.checks.passed ? chalk.green("tests passed") : run.checks.passed === false ? chalk.red("tests failed")
      : chalk.yellow(`tests not run`);
    lines.push(`  ${verdict}${run.slop?.score !== undefined ? chalk.gray(`  ·  slop ${run.slop.score}/100`) : ""}`);
  }
  if (run.status === "ready") lines.push(chalk.cyan("  The pull request is waiting for your approval in the app."));
  if (run.pr?.url) lines.push(`  PR: ${run.pr.url}`);
  if (run.error) lines.push(chalk.red(`  ${run.error}`));
  return lines.join("\n") + "\n";
}

export function formatReview(review: any): string {
  const tone: Record<string, (s: string) => string> = { high: chalk.red, medium: chalk.yellow, low: chalk.gray };
  const lines = [chalk.bold(`\n  ${review.repo}#${review.number}`) + chalk.gray(`  ${review.summary}`)];
  for (const f of review.findings ?? []) {
    lines.push(`  ${(tone[f.severity] ?? chalk.white)(f.severity.padEnd(6))} ${f.title} ${chalk.gray(`${f.path}${f.line ? ":" + f.line : ""}`)}`);
  }
  if (review.escalate) lines.push(chalk.yellow(`  Needs a human look: ${review.reasons.join("; ")}`));
  lines.push(chalk.cyan("  Approve it in the app to post it on GitHub."));
  return lines.join("\n") + "\n";
}

function api(): CoworkerApi {
  const settings = loadSettings();
  if (!settings) {
    console.error(chalk.red("Not signed in. Run `anote coworker login --token ogn_…` or set OUROGEN_TOKEN."));
    process.exit(1);
  }
  return new CoworkerApi(settings);
}

async function guard(fn: () => Promise<void>): Promise<void> {
  try {
    await fn();
  } catch (e) {
    console.error(chalk.red(`  ${(e as Error).message}`));
    process.exit(1);
  }
}

export function coworkerCommand(): Command {
  const cmd = new Command("coworker").description("Hand work to your Ourogen AI coworker (engineer, reviewer, scorecard)");

  cmd.command("login")
    .description("Save a personal access token (Coworker → Settings → API tokens)")
    .requiredOption("--token <token>", "token starting with ogn_")
    .option("--url <url>", "your Ourogen server", DEFAULT_URL)
    .action((opts) => {
      if (!String(opts.token).startsWith("ogn_")) {
        console.error(chalk.red("That isn't a coworker token (they start with ogn_)."));
        process.exit(1);
      }
      const file = saveSettings({ token: opts.token, url: String(opts.url).replace(/\/$/, "") });
      console.log(chalk.green(`Saved to ${file}`));
    });

  cmd.command("engineer")
    .description("Hand a ticket or a description to the AI engineer")
    .argument("<work...>", "jira:ACME-142, ACME-142, notion:<id>, github:owner/repo#12, or a description")
    .option("--repo <owner/name>", "repository (defaults to your coworker's)")
    .option("--plan-only", "stop after the spec and plan, so you can edit them in the app")
    .option("--json", "print the run as JSON")
    .action((words: string[], opts) => guard(async () => {
      const run = await api().handOff({ ...workInput(words), repo: opts.repo }, !opts.planOnly, 3000, (r) => {
        if (!opts.json) console.log(chalk.dim(`  ${r.status}: ${r.title}`));
      });
      console.log(opts.json ? JSON.stringify(run, null, 2) : formatRun(run));
    }));

  cmd.command("review")
    .description("Review a pull request against your standards")
    .argument("<pr>", "owner/repo#37 or a GitHub PR URL")
    .option("--json", "print the review as JSON")
    .action((ref: string, opts) => guard(async () => {
      const pr = parsePrRef(ref);
      if (!pr) throw new Error("Use owner/repo#number or a GitHub pull request URL");
      const review = await api().call("POST", "/reviews", pr);
      console.log(opts.json ? JSON.stringify(review, null, 2) : formatReview(review));
    }));

  cmd.command("runs")
    .description("Recent AI engineer runs")
    .action(() => guard(async () => {
      const { runs } = await api().call<{ runs: any[] }>("GET", "/engineer/runs");
      if (!runs.length) console.log(chalk.gray("  No runs yet."));
      for (const r of runs.slice(0, 15)) console.log(`  ${chalk.cyan(String(r.id).padStart(4))}  ${r.status.padEnd(11)} ${r.title}`);
    }));

  cmd.command("scorecard")
    .description("Work done per unit of time")
    .option("--days <n>", "how many days", "7")
    .option("--csv", "print CSV")
    .action((opts) => guard(async () => {
      const days = Number(opts.days) || 7;
      if (opts.csv) {
        process.stdout.write(await api().call<string>("GET", `/scorecard?days=${days}&format=csv`));
        return;
      }
      const c = await api().call("GET", `/scorecard?days=${days}`);
      console.log(chalk.bold(`\n  Last ${c.days} days`) + chalk.gray(`  ${c.totalOutput} pieces of work, ~${c.humanAttentionHours}h of your attention`));
      for (const [k, v] of Object.entries(c.output as Record<string, number>)) if (v) console.log(`   ${k.padEnd(16)} ${v}`);
      console.log(chalk.gray(`  Cost $${c.cost.totalUsd} vs ~$${Math.round(c.vsHire.hireCostUsd)} for a ${c.vsHire.roleLabel.toLowerCase()} (benchmark)\n`));
    }));

  return cmd;
}
