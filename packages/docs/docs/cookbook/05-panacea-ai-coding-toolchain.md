# Panacea AI Coding Toolchain

This recipe explains how Panacea’s AI coding experience is delivered across CLI, SDK, and VS Code.

## What you'll learn

- The different AI coding entry points in Panacea
- How the CLI, SDK, and VS Code extension relate to the shared backend
- Key product capabilities for private code assistance
- Where to look in the repo for implementation details

## Why this matters

Panacea is built as a unified product with multiple interfaces:

- a **CLI** that powers `anote chat`, code search, and repo review
- a **VS Code extension** for in-editor AI assistance
- a **SDK** for embedding Panacea into other applications

These interfaces share a backend and agent-driven reasoning layer, which makes the product consistent across desktop, web, and code workflows.

## Key Panacea files

| File | Why it matters |
|---|---|
| `Panacea/packages/cli` | TypeScript CLI implementation for developer workflows |
| `Panacea/packages/vscode` | VS Code extension and chat integration |
| `Panacea/packages/sdk` | TypeScript SDK for programmatic access |
| `Panacea/packages/backend` | Shared backend service powering all UI and CLI interactions |

## How it works

- A coding user action starts at the CLI, SDK, or VS Code extension.
- The request is sent to Panacea’s backend API.
- The backend uses agent orchestration and model providers to produce code-aware answers.
- The response is returned in the same interface, with code suggestions, explanations, or fixes.

## Useful product features

- **CLI**: `anote chat`, repo search, code review, code generation, and embeddings-powered assistance.
- **VS Code**: inline chat, diff previews, code actions, and streaming responses.
- **SDK**: a client wrapper for the Panacea API, enabling custom integrations.

## Run it locally

From the workspace root (`anote/panacea`):

```bash
cd Panacea
cp packages/backend/.env.example packages/backend/.env
docker compose up --build
```

This starts the shared backend and frontend services.

In another terminal, run the CLI package:

```bash
cd Panacea/packages/cli
npm install
npm run dev
```

Then you can use the CLI locally or build it with `npm run build`.

For VS Code development, open `Panacea/packages/vscode` in VS Code and launch the extension with the debugger.

## Notes for the cookbook

This recipe is useful for teammates who need a high-level walkthrough of Panacea’s multi-interface AI coding product. It can also point readers to implementation files they can modify or extend.
