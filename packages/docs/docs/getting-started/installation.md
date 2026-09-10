# Installation

## Web app

Open [Ourogen Chat](https://chat.ourogen.ai) to use the hosted app. No installation is needed. For your first conversation, see the [web app guide](../web/overview.md).

## CLI

```bash
npm install -g @anote-ai/anote
```

Requires Node.js 20.19 or later.

## VS Code Extension

Search for **"Anote"** in the VS Code Extensions marketplace, or install via:

```bash
code --install-extension Anote.anote-ai-coding
```

## Web App (Self-hosted)

```bash
git clone https://github.com/anote-ai/Autonomous-Intelligence
cd Autonomous-Intelligence
cp backend/.env.example backend/.env
# Edit .env with your API keys
docker compose up --build
```

Frontend: http://localhost:3000 · Backend: http://localhost:5000

## Desktop App

Download the latest release from [GitHub Releases](https://github.com/anote-ai/Autonomous-Intelligence/releases).

Available for: **macOS** (DMG), **Windows** (installer), **Linux** (AppImage/DEB/RPM).

## Python SDK

```bash
pip install anote-ai
```

## TypeScript/JavaScript SDK

```bash
npm install @anote-ai/sdk
```
