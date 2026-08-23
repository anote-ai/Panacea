# Desktop-App-Installation

## Herunterladen

Laden Sie die neueste Version für Ihre Plattform von der GitHub-Release-Seite herunter.

| Plattform | Datei |
|----------|------|
| macOS | `Anote-AI-x.x.x.dmg` |
| Windows | `Anote-AI-Setup-x.x.x.exe` |
| Linux (deb) | `anote-ai_x.x.x_amd64.deb` |

## Aus dem Quellcode bauen

```bash
# 1. Bündeln Sie das Python-Backend
cd packages/backend
pip install pyinstaller
pyinstaller ../desktop/app.spec --distpath ../desktop/backend-dist

# 2. Bauen und paketieren Sie die Electron-App
cd packages/desktop
npm install
npm run make
```

Die paketierte App befindet sich in `packages/desktop/out/`.
