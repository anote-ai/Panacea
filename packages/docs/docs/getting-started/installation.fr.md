# Installation

## CLI

```bash
npm install -g @anote-ai/anote
```

Nécessite Node.js 18 ou version ultérieure.

## Extension VS Code

Recherchez **"Anote"** dans le marché des extensions VS Code, ou installez via :

```bash
code --install-extension anote-ai.anote-ai-coding
```

## Application Web (Auto-hébergée)

```bash
git clone https://github.com/anote-ai/Panacea
cd Panacea
cp packages/backend/.env.example packages/backend/.env
# Modifiez .env avec vos clés API
docker compose up
```

Frontend : http://localhost:3000 · Backend : http://localhost:5000

## Application de Bureau

Téléchargez la dernière version depuis [GitHub Releases](https://github.com/anote-ai/Panacea/releases).

Disponible pour : **macOS** (DMG), **Windows** (installateur), **Linux** (AppImage/DEB/RPM).

## SDK Python

```bash
pip install anote-ai
```

## SDK TypeScript/JavaScript

```bash
npm install @anote-ai/sdk
```
