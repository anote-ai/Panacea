# Instalasi

## CLI

```bash
npm install -g @anote-ai/anote
```

Membutuhkan Node.js 18 atau lebih baru.

## Ekstensi VS Code

Cari **"Anote"** di pasar Ekstensi VS Code, atau instal melalui:

```bash
code --install-extension anote-ai.anote-ai-coding
```

## Aplikasi Web (Di-host sendiri)

```bash
git clone https://github.com/anote-ai/Panacea
cd Panacea
cp packages/backend/.env.example packages/backend/.env
# Edit .env dengan kunci API Anda
docker compose up
```

Frontend: http://localhost:3000 · Backend: http://localhost:5000

## Aplikasi Desktop

Unduh rilis terbaru dari [GitHub Releases](https://github.com/anote-ai/Panacea/releases).

Tersedia untuk: **macOS** (DMG), **Windows** (installer), **Linux** (AppImage/DEB/RPM).

## Python SDK

```bash
pip install anote-ai
```

## TypeScript/JavaScript SDK

```bash
npm install @anote-ai/sdk
```
