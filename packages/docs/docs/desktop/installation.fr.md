# Installation de l'application de bureau

## Téléchargement

Téléchargez la dernière version pour votre plateforme depuis la page des versions GitHub.

| Plateforme | Fichier |
|------------|---------|
| macOS      | `Anote-AI-x.x.x.dmg` |
| Windows    | `Anote-AI-Setup-x.x.x.exe` |
| Linux (deb)| `anote-ai_x.x.x_amd64.deb` |

## Construction à partir des sources

```bash
# 1. Regrouper le backend Python
cd packages/backend
pip install pyinstaller
pyinstaller ../desktop/app.spec --distpath ../desktop/backend-dist

# 2. Construire et empaqueter l'application Electron
cd packages/desktop
npm install
npm run make
```

L'application empaquetée se trouve dans `packages/desktop/out/`.
