# AI engineer

Hand your coworker engineering work the way you'd hand it to a teammate: a chat message, a Jira ticket, a Notion page or a GitHub issue. It works the way **you** work (from your [knowledge pack](knowledge-packs.md)), and nothing is pushed until you approve the pull request.

```
spec  →  task graph  →  auto-prompted coding  →  tests in a sandbox  →  AI review + slop checks  →  PR (your approval)
```

## Try it in the demo (2 minutes, no API keys)

The demo workspace has a fictional billing service, `anote-demo/acme-api`, with a history of pull requests, review comments, Jira tickets and Notion docs.

1. Open **Coworker → Engineer** and click **Try the demo ticket (ACME-142)**.
2. **Spec.** It reads ACME-142 ("Annual billing: two months free when paying yearly") and drafts a goal, four acceptance criteria, and constraints. Edit anything, then click **Looks right, plan it**.
3. **Task graph.** Three tasks in two steps: implement `annual_quote` in `app/pricing.py`, then (in parallel) tests and the README. Edit the plan in the API if you want a different breakdown.
4. **Start the work.** It writes each task, runs the repo's tests in a sandbox (6 pass), reviews its own change against your standards, and scores it for slop.
5. **Your approval.** An **Open pull request** card shows the branch, files and full diff. Approve it and the run shows the PR link. (In the demo, nothing is pushed.)

Without a model, only the demo ticket works: other specs stop at **Needs a model**. Add an API key in **Settings → Models**, or run a free local model with Ollama.

## From chat, code, or the terminal

- **Chat:** "Take ACME-142 and open a PR when the tests pass." The chat shows the spec and plan, and the pull request card arrives in the same chat when it's ready. "Review #37" reviews a pull request. "How much did you get done this week?" shows the scorecard.
- **SDK:** `new CoworkerClient({ token }).engineer.handOff({ source: "jira:ACME-142" })` ([TypeScript SDK](../../sdk/typescript.md#your-ai-coworker)).
- **CLI:** `anote coworker engineer ACME-142`, `anote coworker review acme/api#37`, `anote coworker scorecard`.

The SDK and CLI use an [API token](../api.md#api-tokens). Tokens can start work and read results, but the pull request still waits for your approval in the app.

## Each step

| Step | What happens | You can |
|---|---|---|
| **Spec** | The request becomes `{goal, acceptance_criteria, constraints, repo}`. Criteria come from the ticket's "Acceptance criteria" list, or from the sentences that state requirements. With a model, it sharpens them into testable criteria and never adds requirements you didn't ask for. | Edit every field before planning |
| **Task graph** | The spec becomes a small dependency graph (`interface`, `impl`, `test`, `docs`, …). Files are picked by matching the spec against the repo's code. Tasks in the same step don't depend on each other and run in parallel. | Replace the graph (`PATCH /engineer/runs/<id>/graph`); cycles and unknown dependencies are rejected |
| **Coding** | Each task is a prompt built from the acceptance criteria it covers, the current files, the repo tree, and your knowledge pack's rules and playbooks. The model returns full file contents and cites the pack items it followed. | See which rules each task followed |
| **Checks** | The repo's tests run against the change (`pytest`, `npm test`, `go test`, `cargo test`, or your **Test command**). Failures go back to the model with the output, up to 2 fix attempts. | Set the test command |
| **Review** | The [AI code reviewer](code-review.md) reviews the change, and the [slop checks](evals.md#slop-checks) score it. | Read every finding |
| **PR** | A `github.pr` action: one commit on `ourogen/<slug>-<run>` and a pull request whose body lists the criteria, checks, review summary, slop score, and the rules it followed. | Approve, edit, or reject it like any other action |

## When it waits for you

A PR is an action like an email, so your **autonomy** for "Open a pull request" applies (default: ask me first). Even at **Just do it**, it always waits when:

- the tests failed,
- the reviewer escalated (a high-severity finding, auth/payments/security code, or the reviewer wasn't sure), or
- the slop score is below your **minimum slop score** (default 70).

## Settings

**Coworker → Engineer → Engineer settings**: default repository, test command, and minimum slop score (`default_repo`, `test_command`, `engineer_min_slop_score` in `PATCH /api/coworker` settings).

## Running tests on real repositories

The demo repo's tests always run. For real repositories, set `COWORKER_SANDBOX=1`: each run clones the repo (with the connected GitHub token) into a temp directory, overlays the change, and runs the tests with a stripped environment and a timeout (`COWORKER_SANDBOX_TIMEOUT`, default 300s). This executes the repository's code, so run the worker in its own container when you turn it on. Without it, checks show as "not run" and the PR says so.

## Cost

Every model call in a run is metered. The run shows its cost, and the activity log records each step.

## Code

`coworker/engineering/`: `spec.py`, `graph.py`, `runs.py` (pipeline and prompts), `sandbox.py`, `review.py`, `slop.py`, `diffs.py`, `demo.py`.
