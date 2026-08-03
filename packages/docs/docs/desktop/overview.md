# Desktop App Overview

The Anote AI desktop app is a private, offline-capable AI assistant built with Electron.

## Key Properties

- **Private**: all data stays on your machine
- **Offline capable**: works with local Ollama models
- **Cross-platform**: Windows, macOS, Linux
- **Bundled backend**: Python Flask backend is packaged as a standalone executable

## Architecture

```
Electron shell
  └─ React frontend (Vite + Tailwind)
  └─ Bundled Python backend (PyInstaller executable)
       └─ Flask API on port 5099
       └─ SQLite database (local)
       └─ ChromaDB vector store (local)
```

## Using the app

1. [Install](installation.md) and launch it — the Electron shell starts the bundled backend automatically
2. Register a local account (this account and its data live only in the local SQLite database, not the hosted service)
3. Pick a model from the dropdown (`claude-sonnet-4-6`, `claude-haiku-4-5-20251001`, `gpt-4o`, or `gpt-4o-mini`) and start chatting — nothing leaves your machine except the request to whichever provider you chose
4. For fully offline use, see [Local Models](local-models.md) — the backend can route to Ollama, though picking one isn't wired into this dropdown yet
