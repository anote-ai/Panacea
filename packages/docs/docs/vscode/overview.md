# VS Code Extension

The Anote VS Code extension provides inline AI assistance directly in your editor.

## Features

- **Chat sidebar** — persistent AI chat panel with session history
- **CodeLens actions** — Explain / Fix / Tests / Refactor above every function
- **Context injection** — add selected code or files to the chat
- **Semantic search** — search your codebase from the command palette
- **Inline diff review** — accept or reject AI edits file-by-file
- **File attachment** — attach images, PDFs, and text files to chat

## Installation

Search for **"Anote"** in the VS Code Extensions marketplace.

Or via CLI:

```bash
code --install-extension anote-ai.anote-ai-coding
```

## Quick Setup

1. Open VS Code
2. Run `Anote: Set Up` from the command palette (`Ctrl+Shift+P`)
3. Choose a mode:
   - **Direct** — pick a provider (`anthropic`, `openai`, `gemini`, `llama`, `xai`, `custom`) and enter its API key
   - **Server** — point `anote.serverUrl` at an Anote backend (local or hosted) instead
4. Open the chat panel from the Activity Bar and send a message
5. Select code and use the right-click **Anote AI** submenu (or CodeLens actions above a function) to explain, fix, refactor, or generate tests for it

See [Settings](settings.md) for the full list of configuration options.
