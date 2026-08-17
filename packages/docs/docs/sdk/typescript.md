# TypeScript SDK

`@anote-ai/sdk` is a typed TypeScript/JavaScript client for the Anote REST API. Use it when you want to call Anote programmatically — from a script, a backend service, or your own app — instead of going through the CLI or web app.

!!! note "Talking to a local backend"
    By default the client points at `https://api.anote.ai`. If you're running the backend from this repo locally (`docker compose up`, or `make dev-backend`), pass `baseUrl: "http://localhost:5050"` (or `:5000` if you're not using the port override) — see [Getting Started → Configuration](../getting-started/configuration.md).

## What you'll need

- Node.js 18+
- An Anote account (register via `POST /auth/register` or the web app's Register page)
- An API key (Step 2 below)

## 1. Install

```bash
npm install @anote-ai/sdk
```

## 2. Get an API key

There's no Settings UI for API keys yet, so mint one directly against the backend. First log in to get a JWT, then use it to create a key:

```bash
# Log in to get a JWT
curl -X POST http://localhost:5050/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "you@example.com", "password": "..."}'
# → { "access_token": "eyJ..." }

# Use the JWT to mint an API key
curl -X POST http://localhost:5050/api/user/api-keys \
  -H "Authorization: Bearer eyJ..."
# → { "key": "ak-..." }
```

Save that `ak-...` value — it's only returned once, at creation time.

## 3. Initialize the client

```ts
import { AnoteClient } from "@anote-ai/sdk";

const client = new AnoteClient({
  apiKey: "ak-...",
  baseUrl: "http://localhost:5050", // omit to use https://api.anote.ai
});
```

`apiKey` is the only required option. Leave out `baseUrl` when you're pointed at the production API.

## 4. Send your first message

```ts
const { result, usage } = await client.chat("Explain this codebase");

console.log(result);
console.log(`Used ${usage.inputTokens} input / ${usage.outputTokens} output tokens`);
```

`chat()` is the non-streaming call — it waits for the full response, which is what you want for scripting and automation. Pass `cwd`, `model`, or `tools` in the second argument to scope the working directory, pick a model, or restrict which tools the AI may use:

```ts
await client.chat("List TODOs in this file", {
  cwd: "/path/to/project",
  model: "claude-sonnet-4-6",
  tools: ["Read", "Grep"],
});
```

## Common tasks

**List and inspect past sessions**

```ts
const sessions = await client.listSessions();
const { history } = await client.getSessionMessages(sessions[0].sessionId);
```

**Search across session history**

```ts
const { results } = await client.search("authentication logic");
```

**Check your usage and quota**

```ts
const usage = await client.getUsage();
console.log(`${usage.remaining.requests} requests remaining this month`);
```

**Share a session as a read-only link**

```ts
const { shareUrl } = await client.shareSession(sessions[0].sessionId);
```

**Handle errors**

Every non-2xx response throws `AnoteError`, which carries the HTTP status and parsed response body:

```ts
import { AnoteClient, AnoteError } from "@anote-ai/sdk";

try {
  await client.chat("...");
} catch (err) {
  if (err instanceof AnoteError) {
    console.error(err.status, err.message); // e.g. 429, "Monthly quota exceeded"
  }
}
```

**Check server liveness (no auth required)**

```ts
const health = await client.health();
```

## API reference

### `new AnoteClient(options)`

| Option | Type | Required | Description |
|---|---|---|---|
| `apiKey` | `string` | ✓ | API key from Step 2, starts with `ak-` |
| `baseUrl` | `string` | | Server URL (default: `https://api.anote.ai`) |

### Methods

| Method | Description |
|--------|-------------|
| `chat(message, options?)` | Send a message, get a complete AI response |
| `listSessions()` | List all chat sessions |
| `getSessionMessages(id)` | Get message history for a session |
| `deleteSession(id)` | Delete a session |
| `shareSession(id)` | Mint a shareable read-only link |
| `search(query, limit?)` | Full-text search across sessions |
| `getUsage()` | Current month usage + quota |
| `health()` | Server liveness check (no auth needed) |

## Next steps

- [Backend API Overview](../api/overview.md) — the REST endpoints underneath this SDK
- [CLI Overview](../cli/overview.md) — for interactive/terminal use instead of scripting
