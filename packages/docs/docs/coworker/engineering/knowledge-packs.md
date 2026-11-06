# Knowledge packs

A knowledge pack is what your AI knows about **how you work**. It's built from your own work in the tools you connect, and it's what makes the AI engineer and code reviewer work like you instead of like a generic model.

Open **Coworker → Knowledge**.

## What's in it

| Part | Learned from | Example |
|---|---|---|
| **Skills** | Files you touched in your PRs (languages, CI, Docker, tests) and the domains in your PRs, tickets and docs | Python · Testing · Billing & payments |
| **Style rules** | Review comments you left, and convention pages in Notion | "Money is Decimal, never float." with the review comment that taught it |
| **Playbooks** | Your PRs grouped by kind (`fix:`, `feat:`, `refactor:`…), plus "How I…", playbook, runbook and postmortem pages | **Fixing a bug**: reproduce it with a failing test → smallest change → add tests → open the PR |

Every item links to its evidence: the PRs, review comments, tickets or pages it came from. With a model, it also suggests a few rules and playbooks the heuristics missed (marked as model-suggested).

Rules in a known category carry a **check** the [code reviewer](code-review.md) runs: tests, money as Decimal, specific exceptions, naming, one change per PR, early returns, no skipped tests, docs updated.

## You're in control

- **Edit, remove or add** any skill, rule or playbook. Your edits survive every rebuild, and removed items never come back.
- **Rebuild** after new work syncs.
- **Disconnecting** GitHub, Jira or Notion deletes what was synced from it and rebuilds the pack without it.
- **Scrubbed**: secrets (GitHub, Anthropic, AWS, Slack, HubSpot and Notion tokens, private keys, `password=…`), other people's email addresses and phone numbers are removed before anything enters the pack.

## Versions

**Save version** freezes the current pack as version 1, 2, 3… A saved version never changes. It's what a [marketplace](marketplace.md) listing points to, so buyers get the same AI you published.

## Sources

Connect them in **Settings → Developer tools** ([how](dev-tools.md)). The demo workspace comes with a fictional engineer's history, so you can see a full pack without connecting anything.

## API

`GET /knowledge-pack`, `POST /knowledge-pack/build`, `PATCH /knowledge-pack` (`{"section": "skills" | "style_rules" | "playbooks", "op": "update" | "remove" | "add", "id", "values"}`), `GET`/`POST /knowledge-pack/versions`.

Code: `coworker/knowledge_pack.py`.
