# Installation

## CLI

```bash
npm install -g @anote-ai/anote
```

Benötigt Node.js 18 oder höher.

## VS Code Erweiterung

Suchen Sie nach **"Anote"** im VS Code Erweiterungsmarktplatz oder installieren Sie über:

```bash
code --install-extension anote-ai.anote-ai-coding
```

## Webanwendung (Selbstgehostet)

```bash
git clone https://github.com/anote-ai/Panacea
cd Panacea
cp packages/backend/.env.example packages/backend/.env
# Bearbeiten Sie .env mit Ihren API-Schlüsseln
docker compose up
```

Frontend: http://localhost:3000 · Backend: http://localhost:5000

## Desktop-Anwendung

Laden Sie die neueste Version von [GitHub Releases](https://github.com/anote-ai/Panacea/releases) herunter.

Verfügbar für: **macOS** (DMG), **Windows** (Installer), **Linux** (AppImage/DEB/RPM).

## Python SDK

```bash
pip install anote-ai
```

## TypeScript/JavaScript SDK

```bash
npm install @anote-ai/sdk
```
