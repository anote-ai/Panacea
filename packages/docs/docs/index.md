# Overview

**Anote AI** is a unified AI coding assistant and private chatbot platform. It reads your codebase, edits files, runs commands, reviews PRs, and answers questions over your documents — available in your terminal, IDE, browser, desktop app, and phone.

## Get started

Anote runs on several surfaces: the CLI, VS Code, the web, desktop, and mobile. Pick one below to get going. Most surfaces talk to the hosted Anote backend or your own self-hosted instance (see [Configuration](getting-started/configuration.md)).

=== "CLI"

    The full-featured CLI for working with Anote directly in your terminal. Ask questions, fix bugs, review PRs, and search your codebase without leaving the shell.

    ```bash
    npm install -g @anote-ai/anote
    ```

    Requires Node.js 18 or later. Then, in any project:

    ```bash
    cd your-project
    anote init
    anote ask "explain this codebase"
    ```

    `anote init` walks you through setting your API key and preferred LLM provider.

    [Continue with the Quick Start →](getting-started/quickstart.md)

=== "VS Code"

    The VS Code extension brings a chat sidebar, inline diff review, and streaming responses directly into your editor.

    Search for **"Anote"** in the VS Code Extensions marketplace, or install via:

    ```bash
    code --install-extension anote-ai.anote-ai-coding
    ```

    [VS Code Extension overview →](vscode/overview.md)

=== "Web App"

    A ChatGPT-style browser chat interface with document upload and RAG-backed Q&A. Self-host it with Docker Compose:

    ```bash
    git clone https://github.com/anote-ai/Panacea
    cd Panacea
    cp packages/backend/.env.example packages/backend/.env
    # Edit .env with your API keys
    docker compose up
    ```

    Frontend: `http://localhost:3000` · Backend: `http://localhost:5000`

    [Web App overview →](web/overview.md)

=== "Desktop"

    A private, offline-capable Electron app. All data stays on your machine, and it works with local Ollama models when you don't want to call out to a hosted provider.

    Download the latest release from [GitHub Releases](https://github.com/anote-ai/Panacea/releases) — available for **macOS** (DMG), **Windows** (installer), and **Linux** (AppImage/DEB/RPM).

    [Desktop App overview →](desktop/overview.md)

=== "Mobile"

    A native iOS and Android chat client built with Expo.

    ```bash
    cd packages/mobile
    npm install
    npx expo start
    ```

    Scan the QR code with the Expo Go app, or run in a simulator.

    [Mobile App overview →](mobile/overview.md)

## What you can do

??? abstract "Ask questions about your codebase"

    ```bash
    anote ask "how does the authentication middleware work?"
    anote ask --file src/auth.ts "explain this file"
    anote ask --compare               # side-by-side across multiple models
    cat src/handler.py | anote ask "what could go wrong here?"
    ```

??? bug "Fix bugs automatically"

    `anote fix --loop` iterates against your test suite — up to `--max-iterations` rounds — until it passes, or fixes a single file with `--file`.

    ```bash
    anote fix --loop --max-iterations 5
    ```

??? example "Review pull requests"

    ```bash
    anote review --pr 42
    ```

    Reviews for bugs, security issues, and quality — locally against a directory/file, or posted straight to a GitHub PR.

??? search "Search your codebase semantically"

    ```bash
    anote index              # build a TF-IDF index (run once, then keep updated)
    anote search "JWT token validation"
    ```

??? question "Chat and Q&A over your documents"

    Upload documents in the [Web App](web/overview.md) or [Desktop App](desktop/overview.md) and ask questions against them — RAG-backed via `POST /api/documents/{id}/ask`.

??? tip "Audit for security and performance issues"

    ```bash
    anote security --severity high --fix
    anote perf --focus "database,bundle" --fix
    ```

??? note "Generate changelogs and docs, or run migrations"

    ```bash
    anote changelog --since v1.2.0
    anote docs src/api.ts --style jsdoc
    anote migrate --from "React 17" --to "React 18"
    ```

??? info "Check your setup"

    ```bash
    anote doctor
    ```

    Checks Node.js ≥ 18, `ANTHROPIC_API_KEY`, `.anote.json`, `CLAW.md`, and git.

## Use Anote everywhere

| I want to... | Best option |
|---|---|
| Work from my terminal | [CLI](cli/overview.md) |
| Get inline AI help in my editor | [VS Code Extension](vscode/overview.md) |
| Chat with documents in a browser | [Web App](web/overview.md) |
| Keep everything private and offline | [Desktop App](desktop/overview.md) — works with local Ollama models |
| Chat from my phone | [Mobile App](mobile/overview.md) |
| Call Anote from my own code or scripts | [TypeScript SDK](sdk/typescript.md) or [Python SDK](sdk/python.md) |
| Integrate directly against the REST API | [Backend API](api/overview.md) |
| Automate PR review or CI checks | [CLI: `anote review --pr`](cli/commands.md#anote-review) |

## Supported LLM providers

- **Anthropic** — Claude (`claude-opus-4-8`, `claude-sonnet-4-6`, `claude-haiku-4-5`)
- **OpenAI** — GPT-4o, GPT-4o-mini
- **Google** — Gemini 2.0 Flash, Gemini 1.5 Pro
- **Ollama** — any local model (Llama 3, Mistral, etc.)
- **xAI** — Grok

## Next steps

- [Quick Start](getting-started/quickstart.md) — init, ask, fix, index, review, and changelog in order
- [How Panacea Works](core-concepts/how-it-works.md) — the agentic loop, tools, and streaming
- [Permission Modes](use-panacea/permission-modes.md) — control what the agent can do without asking
- [Common Workflows](use-panacea/common-workflows.md) — step-by-step patterns for everyday tasks
- [Configuration](getting-started/configuration.md) — API keys, provider setup, and `~/.anote/config.json`
- [CLI Commands](cli/commands.md) — the full command reference
- [Backend API](api/overview.md) — the REST endpoints powering every surface
- [Architecture](development/architecture.md) — how the monorepo and backend fit together
- [Contributing](development/contributing.md) — set up the repo for local development
