# Installazione dell'App Desktop

## Download

Scarica l'ultima versione per la tua piattaforma dalla pagina delle release di GitHub.

| Piattaforma | File |
|-------------|------|
| macOS       | `Anote-AI-x.x.x.dmg` |
| Windows     | `Anote-AI-Setup-x.x.x.exe` |
| Linux (deb) | `anote-ai_x.x.x_amd64.deb` |

## Compilazione dal Codice Sorgente

```bash
# 1. Impacchetta il backend Python
cd packages/backend
pip install pyinstaller
pyinstaller ../desktop/app.spec --distpath ../desktop/backend-dist

# 2. Compila e impacchetta l'app Electron
cd packages/desktop
npm install
npm run make
```

L'app impacchettata si trova in `packages/desktop/out/`.
