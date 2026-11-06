/**
 * Your Ourogen AI coworker in VS Code: hand tickets (or the selected code) to the AI engineer,
 * run the AI code reviewer on a pull request (findings show up as diagnostics), and see the scorecard.
 *
 * Uses a personal access token (Coworker → Settings → API tokens), kept in VS Code's secret storage.
 * Tokens can't approve anything: pull requests and reviews wait for you in the app.
 */
import * as vscode from "vscode";
import { execFile } from "child_process";
import * as path from "path";
import { CoworkerApi, findingsByFile, parsePrRef, repoFromRemote, selectionTask, summarizeRun, workInput } from "./coworkerCore";

const SECRET = "anote.coworkerToken";
const DEFAULT_URL = "https://chat.ourogen.ai";

function coworkerUrl(): string {
  return (vscode.workspace.getConfiguration("anote").get<string>("coworkerUrl") || DEFAULT_URL).replace(/\/$/, "");
}

async function workspaceRepo(): Promise<string> {
  const folder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
  if (!folder) return "";
  return new Promise((resolve) => {
    execFile("git", ["config", "--get", "remote.origin.url"], { cwd: folder }, (err, stdout) => resolve(err ? "" : repoFromRemote(stdout)));
  });
}

export function registerCoworker(context: vscode.ExtensionContext): void {
  const output = vscode.window.createOutputChannel("Ourogen coworker");
  const diagnostics = vscode.languages.createDiagnosticCollection("ourogen-review");
  context.subscriptions.push(output, diagnostics);

  async function client(): Promise<CoworkerApi | undefined> {
    const token = await context.secrets.get(SECRET);
    if (token) return new CoworkerApi({ url: coworkerUrl(), token });
    const pick = await vscode.window.showWarningMessage("Sign in to your AI coworker first.", "Sign in");
    if (pick) await vscode.commands.executeCommand("anote.coworker.signIn");
    return undefined;
  }

  const openInApp = (tab: string) => vscode.env.openExternal(vscode.Uri.parse(`${coworkerUrl()}/app/coworker/${tab}`));

  async function handOff(input: { source?: string; text?: string }, label: string): Promise<void> {
    const api = await client();
    if (!api) return;
    const repo = await workspaceRepo();
    await vscode.window.withProgress(
      { location: vscode.ProgressLocation.Notification, title: `AI engineer: ${label}`, cancellable: true },
      async (progress, cancel) => {
        try {
          const run = await api.handOff({ ...input, ...(repo ? { repo } : {}) }, (r) => {
            progress.report({ message: r.status === "running" ? "writing code and running tests…" : r.status });
          }, () => cancel.isCancellationRequested);
          output.appendLine(`\n[${new Date().toLocaleTimeString()}]`);
          summarizeRun(run).forEach((l) => output.appendLine(l));
          if (run.status === "ready") {
            const pick = await vscode.window.showInformationMessage(
              `The pull request for “${run.title}” is ready for your approval.`, "Review and approve", "Show details");
            if (pick === "Review and approve") openInApp("engineer");
            if (pick === "Show details") output.show(true);
          } else if (cancel.isCancellationRequested) {
            vscode.window.showInformationMessage("Still running in the background. Follow it in Coworker → Engineer.");
          } else {
            output.show(true);
            vscode.window.showWarningMessage(`AI engineer: ${run.status}${run.error ? ` (${run.error})` : ""}`);
          }
        } catch (e) {
          vscode.window.showErrorMessage(`AI engineer: ${(e as Error).message}`);
        }
      });
  }

  context.subscriptions.push(
    vscode.commands.registerCommand("anote.coworker.signIn", async () => {
      const url = await vscode.window.showInputBox({ prompt: "Your Ourogen server", value: coworkerUrl(), ignoreFocusOut: true });
      if (url === undefined) return;
      const token = await vscode.window.showInputBox({
        prompt: "Personal access token (Coworker → Settings → API tokens)", password: true, ignoreFocusOut: true,
        validateInput: (v) => (v.startsWith("ogn_") ? undefined : "Coworker tokens start with ogn_"),
      });
      if (!token) return;
      await vscode.workspace.getConfiguration("anote").update("coworkerUrl", url.replace(/\/$/, ""), vscode.ConfigurationTarget.Global);
      await context.secrets.store(SECRET, token);
      try {
        await new CoworkerApi({ url, token }).call("GET", "/scorecard?days=1");
        vscode.window.showInformationMessage("Signed in to your AI coworker.");
      } catch (e) {
        vscode.window.showWarningMessage(`Saved, but the server said: ${(e as Error).message}`);
      }
    }),

    vscode.commands.registerCommand("anote.coworker.signOut", async () => {
      await context.secrets.delete(SECRET);
      vscode.window.showInformationMessage("Signed out of your AI coworker. Revoke the token in the app if you no longer need it.");
    }),

    vscode.commands.registerCommand("anote.coworker.handOff", async () => {
      const value = await vscode.window.showInputBox({
        prompt: "A ticket (ACME-142, jira:…, notion:…, github:owner/repo#12) or describe the work",
        placeHolder: "ACME-142", ignoreFocusOut: true,
      });
      if (value?.trim()) await handOff(workInput(value), value.trim().slice(0, 60));
    }),

    vscode.commands.registerCommand("anote.coworker.handOffSelection", async () => {
      const editor = vscode.window.activeTextEditor;
      if (!editor || editor.selection.isEmpty) {
        vscode.window.showWarningMessage("Select the code you want worked on first.");
        return;
      }
      const ask = await vscode.window.showInputBox({ prompt: "What should the AI engineer do with this code?",
        placeHolder: "e.g. Handle partial refunds, with tests", ignoreFocusOut: true });
      if (!ask?.trim()) return;
      const file = vscode.workspace.asRelativePath(editor.document.uri);
      const text = selectionTask(ask, file, editor.selection.start.line + 1, editor.document.getText(editor.selection));
      await handOff({ text }, ask.trim().slice(0, 60));
    }),

    vscode.commands.registerCommand("anote.coworker.reviewPr", async () => {
      const api = await client();
      if (!api) return;
      const repo = await workspaceRepo();
      const ref = await vscode.window.showInputBox({ prompt: "Pull request to review", placeHolder: repo ? `#37 or ${repo}#37` : "owner/repo#37" });
      const pr = ref ? parsePrRef(ref, repo) : null;
      if (!pr) return;
      try {
        const review = await vscode.window.withProgress(
          { location: vscode.ProgressLocation.Notification, title: `Reviewing ${pr.repo}#${pr.number}…` },
          () => api.call("POST", "/reviews", pr));
        diagnostics.clear();
        const root = vscode.workspace.workspaceFolders?.[0]?.uri;
        if (root && pr.repo === repo) {
          for (const [file, items] of findingsByFile(review.findings)) {
            diagnostics.set(vscode.Uri.file(path.join(root.fsPath, file)), items.map((d) => {
              const diag = new vscode.Diagnostic(new vscode.Range(d.line, 0, d.line, 1000), d.message,
                d.severity === "high" ? vscode.DiagnosticSeverity.Error
                  : d.severity === "medium" ? vscode.DiagnosticSeverity.Warning : vscode.DiagnosticSeverity.Information);
              diag.source = "Ourogen review";
              return diag;
            }));
          }
        }
        output.appendLine(`\n${pr.repo}#${pr.number}: ${review.summary}${review.escalate ? ` Needs a human: ${review.reasons.join("; ")}` : ""}`);
        for (const f of review.findings) output.appendLine(`  ${f.severity.padEnd(6)} ${f.title}  ${f.path}${f.line ? ":" + f.line : ""}`);
        const pick = await vscode.window.showInformationMessage(
          `${review.summary}${root && pr.repo === repo ? " Findings are in the Problems panel." : ""}`, "Post it (in the app)", "Show details");
        if (pick === "Post it (in the app)") openInApp("approvals");
        if (pick === "Show details") output.show(true);
      } catch (e) {
        vscode.window.showErrorMessage(`AI review: ${(e as Error).message}`);
      }
    }),

    vscode.commands.registerCommand("anote.coworker.scorecard", async () => {
      const api = await client();
      if (!api) return;
      try {
        const c = await api.call("GET", "/scorecard?days=7");
        output.appendLine(`\nLast 7 days: ${c.totalOutput} pieces of work, ~${c.humanAttentionHours}h of your attention`);
        for (const [k, v] of Object.entries(c.output as Record<string, number>)) if (v) output.appendLine(`  ${k}: ${v}`);
        output.appendLine(`  Cost $${c.cost.totalUsd} vs ~$${Math.round(c.vsHire.hireCostUsd)} for a ${c.vsHire.roleLabel.toLowerCase()} (benchmark)`);
        output.show(true);
      } catch (e) {
        vscode.window.showErrorMessage(`Scorecard: ${(e as Error).message}`);
      }
    }),
  );
}
