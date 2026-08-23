# Instalação

## CLI

```bash
npm install -g @anote-ai/anote
```

Requer Node.js 18 ou posterior.

## Extensão do VS Code

Pesquise por **"Anote"** no marketplace de Extensões do VS Code, ou instale via:

```bash
code --install-extension anote-ai.anote-ai-coding
```

## Aplicativo Web (Auto-hospedado)

```bash
git clone https://github.com/anote-ai/Panacea
cd Panacea
cp packages/backend/.env.example packages/backend/.env
# Edite .env com suas chaves de API
docker compose up
```

Frontend: http://localhost:3000 · Backend: http://localhost:5000

## Aplicativo Desktop

Baixe a versão mais recente de [GitHub Releases](https://github.com/anote-ai/Panacea/releases).

Disponível para: **macOS** (DMG), **Windows** (instalador), **Linux** (AppImage/DEB/RPM).

## SDK Python

```bash
pip install anote-ai
```

## SDK TypeScript/JavaScript

```bash
npm install @anote-ai/sdk
```
