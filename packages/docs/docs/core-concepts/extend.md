# Extend Panacea

Two ways to customize how Panacea behaves in your project: **CLAW.md** for persistent instructions, and **hooks** for running your own commands around tool calls.

## CLAW.md — project memory

`CLAW.md` is a markdown file Panacea reads for project context — the same idea as a README aimed at the agent instead of a human. `anote init` generates one automatically, pre-filled with your detected stack and verification commands (test/lint/build):

```markdown
# CLAW.md

This file provides guidance to Anote AI when working with code in this repository.

## Project overview

<!-- Describe what this project does -->

## Stack

TypeScript · Next.js

## Verification

Run these before considering a change complete:

  npm test
  npm run lint

## Working agreement

- Read relevant files before making changes
- Run the verification commands after modifying logic
- Keep changes small and focused
- Prefer editing existing files over creating new ones
```

Edit it freely — add architecture notes, conventions, or things the agent keeps getting wrong. Panacea reads it at the start of every session in that directory.

## Hooks — run your own commands around tool calls

Hooks run a shell command before (`preToolUse`) or after (`postToolUse`) every tool call, configured in `.anote.json`:

```json
{
  "hooks": {
    "preToolUse": ["./scripts/check-tool-policy.sh"],
    "postToolUse": ["npx prettier --write ."]
  }
}
```

**Exit code semantics:**

| Exit code | Effect |
|---|---|
| `0` | Allow — stdout is captured as an informational message |
| `2` | Deny — stdout is captured as the reason, shown to the agent |
| anything else | Warn but allow |

Use `preToolUse` to block risky commands or enforce policy before they run; use `postToolUse` for things like auto-formatting after every edit.

## Next steps

- [Explore the .anote directory](anote-directory.md) — where CLAW.md and config live
- [Permission modes](../use-panacea/permission-modes.md) — the other lever on what the agent can do
