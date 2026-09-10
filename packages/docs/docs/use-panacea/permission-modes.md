# Permission Modes

Ourogen has three permission modes, controlling whether the agent asks before writing files or running commands.

| Mode | Behavior |
|---|---|
| `default` | Confirms before editing files or running non-read-only commands |
| `acceptEdits` | Auto-accepts file edits without asking |
| `bypassPermissions` | Runs everything without confirmation — use with care |

Set it globally or per-project:

```bash
anote config set permissionMode acceptEdits
```

or in `.anote.json`:

```json
{ "permissionMode": "acceptEdits" }
```

## Per-command overrides

Most commands don't require you to touch global config — they take their own flags for the same idea:

| Flag | Available on | Effect |
|---|---|---|
| `--auto` | `fix`, `refactor` | Auto-accept edits for this run only |
| `--dry-run` | `fix`, `docs`, `migrate`, `security`, `perf`, `refactor`, `generate`, `changelog`, `commit`, `review` | Show what would happen without writing anything |
| `--no-edit` | `ask` | Read-only — the agent can't modify files even if it wants to |
| `--yes` | `init` | Skip interactive prompts, accept defaults |

`anote fix --loop` implies `acceptEdits` automatically, since it needs to keep editing across iterations without stopping to ask each time.

## Hooks as a policy layer

For anything more specific than "ask vs. don't ask" — like blocking `Bash` calls that touch a certain path — use a `preToolUse` hook instead. See [Extend Ourogen](../core-concepts/extend.md).

## Next steps

- [How Ourogen works](../core-concepts/how-it-works.md) — the agent loop these modes control
- [Explore the .anote directory](../core-concepts/anote-directory.md) — where `permissionMode` lives in config
