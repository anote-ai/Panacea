# Instalación

## CLI

```bash
npm install -g @anote-ai/anote
```

Requiere Node.js 18 o posterior.

## Extensión de VS Code

Busca **"Anote"** en el mercado de extensiones de VS Code, o instala a través de:

```bash
code --install-extension anote-ai.anote-ai-coding
```

## Aplicación Web (Autoalojada)

```bash
git clone https://github.com/anote-ai/Panacea
cd Panacea
cp packages/backend/.env.example packages/backend/.env
# Edita .env con tus claves API
docker compose up
```

Frontend: http://localhost:3000 · Backend: http://localhost:5000

## Aplicación de Escritorio

Descarga la última versión desde [GitHub Releases](https://github.com/anote-ai/Panacea/releases).

Disponible para: **macOS** (DMG), **Windows** (instalador), **Linux** (AppImage/DEB/RPM).

## SDK de Python

```bash
pip install anote-ai
```

## SDK de TypeScript/JavaScript

```bash
npm install @anote-ai/sdk
```
