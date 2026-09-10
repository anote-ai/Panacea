# Explore the .anote Directory

Ourogen's CLI reads configuration from two places: a per-project file and a global one.

## Project config

Ourogen searches upward from your current directory for the first file it finds, in this order:

- `.anote.json`
- `.claw.json`
- `anote.config.json`

```json
{
  "model": "claude-sonnet-4-6",
  "permissionMode": "default",
  "maxTurns": 20,
  "compactAfterMessages": 40,
  "hooks": {
    "preToolUse": [],
    "postToolUse": []
  }
}
```

| Key | Purpose |
|---|---|
| `model` | Default model for this project |
| `permissionMode` | `default`, `acceptEdits`, or `bypassPermissions` — see [Permission modes](../use-panacea/permission-modes.md) |
| `provider` | Explicit provider override (usually auto-detected from `model`) |
| `baseUrl` | Base URL for OpenAI-compatible endpoints, e.g. `http://localhost:11434/v1` for Ollama |
| `maxTurns` | Turn cap per session |
| `compactAfterMessages` | When to compact session history |
| `hooks` | `preToolUse` / `postToolUse` shell hooks — see [Extend Ourogen](extend.md) |

`anote init` creates `.anote.json` for you. `anote config` reads and writes it:

```bash
anote config              # show effective config (global + local)
anote config get model
anote config set model gpt-4.1
anote config path         # print the global config file path
anote config edit         # open the global config in $EDITOR
```

## Global config

`~/.anote/config.json` holds your defaults — applied whenever a project doesn't override them. Project config always wins over global config.

## CLAW.md

Not JSON — a markdown file the agent reads for project context at the start of every session. See [Extend Ourogen](extend.md) for what goes in it.

## Next steps

- [Permission modes](../use-panacea/permission-modes.md)
- [Manage sessions](../use-panacea/sessions.md)
