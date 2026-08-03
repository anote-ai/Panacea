# VS Code Extension Settings

Configure the extension in VS Code's settings UI (search "Anote") or `settings.json`.

| Setting | Default | Description |
|---------|---------|-------------|
| `anote.provider` | `anthropic` | Provider family: `anthropic`, `openai`, `gemini`, `llama`, `xai`, `custom` |
| `anote.apiKey` | `""` | Provider API key for direct mode. Leave blank when using an Anote server |
| `anote.model` | `claude-sonnet-4-6` | Model id to use for the selected provider |
| `anote.serverUrl` | `""` | URL of an Anote server — set this to route through a hosted/local server instead of the built-in direct runtime |
| `anote.baseUrl` | `""` | Optional provider base URL override for future runtime adapters |
| `anote.autoEdit` | `false` | Automatically accept file edits without confirmation |
| `anote.maxTurns` | `30` | Maximum number of agentic turns per conversation |
| `anote.persistSessions` | `true` | Persist chat history across VS Code reloads |
| `anote.showToolUse` | `true` | Show tool-use indicators in the chat panel while Anote works |
| `anote.enableCodeLens` | `true` | Show inline action buttons (CodeLens) above functions and classes |

```json
{
  "anote.provider": "anthropic",
  "anote.model": "claude-sonnet-4-6",
  "anote.autoEdit": false
}
```

## Direct mode vs. server mode

- **Direct mode** (default): set `anote.provider` + `anote.apiKey`, and the extension calls the model provider directly.
- **Server mode**: set `anote.serverUrl` to point at an Anote backend (local `packages/backend` or hosted) instead — leave `anote.apiKey` blank.
