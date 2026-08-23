# Installazione

## CLI

```bash
npm install -g @anote-ai/anote
```

Richiede Node.js 18 o versioni successive.

## Estensione VS Code

Cerca **"Anote"** nel marketplace delle estensioni di VS Code, oppure installa tramite:

```bash
code --install-extension anote-ai.anote-ai-coding
```

## Web App (Auto-ospitata)

```bash
git clone https://github.com/anote-ai/Panacea
cd Panacea
cp packages/backend/.env.example packages/backend/.env
# Modifica .env con le tue chiavi API
docker compose up
```

Frontend: http://localhost:3000 · Backend: http://localhost:5000

## App Desktop

Scarica l'ultima versione da [GitHub Releases](https://github.com/anote-ai/Panacea/releases).

Disponibile per: **macOS** (DMG), **Windows** (installer), **Linux** (AppImage/DEB/RPM).

## SDK Python

```bash
pip install anote-ai
```

## SDK TypeScript/JavaScript

```bash
npm install @anote-ai/sdk
```
