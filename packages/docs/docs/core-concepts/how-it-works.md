# How Ourogen Works

Ourogen runs an **agentic loop**: it reads your prompt, decides which tools to call, executes them, reads the results, and repeats — streaming its reasoning and edits back to you — until the task is done or it hits a turn limit.

## The tools

By default, Ourogen's agent can call:

| Tool | Purpose |
|---|---|
| `Read` | Read a file |
| `Write` | Create or overwrite a file |
| `Edit` | Make a targeted change to a file |
| `Bash` | Run a shell command |
| `Glob` | Find files by pattern |
| `Grep` | Search file contents |

Some commands narrow this list — `anote review` and `anote diff`, for example, only allow `Read`, `Glob`, `Grep`, and `Bash`, since a review shouldn't write files.

## Turns and compaction

Each tool call/response pair counts as a turn. The agent stops after `maxTurns` (default 30, configurable via `anote config set maxTurns <n>` or `.anote.json`). Long sessions are compacted after `compactAfterMessages` (default 40) to keep the context window manageable.

## Streaming

Every surface — CLI, VS Code, Web, Desktop — talks to the same backend endpoint (`POST /api/chat/stream`), which streams the model's response and tool activity over SSE as it happens. You see file reads, edits, and command output live, not just the final answer.

## Multi-provider

The agent loop isn't tied to one model. `anote ask --compare` runs the same prompt across multiple models side by side, and `--model` on most commands accepts any configured provider (`claude-sonnet-4-6`, `gpt-4.1`, `gemini-2.5-pro`, or a local `ollama/<model>`).

## Next steps

- [Permission modes](../use-panacea/permission-modes.md) — control whether the agent asks before editing or running commands
- [Extend Ourogen](extend.md) — CLAW.md and hooks
- [CLI Commands](../cli/commands.md) — the full command reference
