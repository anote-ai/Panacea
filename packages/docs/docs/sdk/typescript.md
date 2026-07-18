# TypeScript SDK

The `@anote-ai/sdk` package provides a typed client for the Anote backend
REST API — the same API described in [API Reference](../api/overview.md).

## Installation

```bash
npm install @anote-ai/sdk
```

## Usage

```typescript
import { AnoteClient } from '@anote-ai/sdk';

const client = new AnoteClient({
  baseUrl: 'http://localhost:5000',
  apiKey: '<jwt-access-token>',
});

// Non-streaming chat
const { response } = await client.chat('Explain this codebase');
console.log(response);

// Streaming chat
for await (const chunk of client.chatStream('Explain this codebase')) {
  process.stdout.write(chunk);
}

// Codebase search (TF-IDF, requires `anote index` to have run first)
const { results } = await client.search('authentication logic');

// Health check
const health = await client.health();
```

## API Reference

| Method | Description |
|--------|-------------|
| `chat(message, options)` | Send a message, get a complete response |
| `chatStream(message, options)` | Send a message, yield response text chunks over SSE |
| `createSession()` | Create a new chat session, returns its ID |
| `listSessions()` | List all chat session IDs |
| `getSessionMessages(id)` | Get a session's message history |
| `deleteSession(id)` | Delete a session |
| `search(query, options)` | TF-IDF search over the codebase index |
| `health()` | Health check (no auth required) |
