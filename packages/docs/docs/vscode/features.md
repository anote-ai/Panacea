# VS Code Extension Features

## Chat Sidebar

Open the Ourogen chat panel from the activity bar. Ask questions about your codebase, get code suggestions, and review diffs.

## Inline Diff Review

When the agent proposes file changes, a diff view opens automatically. Accept or reject each change individually.

## Streaming Responses

Responses stream token-by-token in real time. A stop button lets you cancel mid-stream.

## Tool Use Visibility

See exactly which files the agent reads, writes, or executes during each response.

## Your AI coworker in the editor

If you use [Ourogen Coworker](../coworker/engineering/index.md), run **Ourogen: Sign In to My AI Coworker** with a personal access token from **Coworker → Settings → API tokens**. The token is kept in VS Code's secret storage, not in your settings.

| Command | What it does |
|---|---|
| **Ourogen: Hand a Ticket to My AI Engineer** | Type `ACME-142` (or `jira:…`, `notion:…`, `github:owner/repo#12`, or a description). It drafts the spec, plans the work, writes the code, runs the tests and reviews itself, with progress in a notification. When the pull request is ready, **Review and approve** opens it in the app. |
| **Ourogen: Hand This Code to My AI Engineer** | Select code, right-click → **Anote AI**, and say what to do with it. The selection and its file go along as context. |
| **Ourogen: AI Review of a Pull Request** | `#37` (your workspace's repository) or `owner/repo#37`. The findings appear as squiggles and in the **Problems** panel, each with its severity, the suggested fix, and the standard it comes from. **Post it (in the app)** sends you to approve the review. |
| **Ourogen: Show My AI Coworker's Scorecard** | The last 7 days of work, in the **Ourogen coworker** output channel. |

The repository is read from your workspace's `origin` remote. Tokens can't approve anything: pull requests and reviews always wait for you in the app. Set `anote.coworkerUrl` if you run your own server.
