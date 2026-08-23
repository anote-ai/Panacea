# Instalação do Aplicativo de Desktop

## Download

Baixe a versão mais recente para sua plataforma na página de lançamentos do GitHub.

| Plataforma | Arquivo |
|------------|---------|
| macOS      | `Anote-AI-x.x.x.dmg` |
| Windows    | `Anote-AI-Setup-x.x.x.exe` |
| Linux (deb)| `anote-ai_x.x.x_amd64.deb` |

## Construindo a Partir do Código Fonte

```bash
# 1. Agrupe o backend em Python
cd packages/backend
pip install pyinstaller
pyinstaller ../desktop/app.spec --distpath ../desktop/backend-dist

# 2. Construa e empacote o aplicativo Electron
cd packages/desktop
npm install
npm run make
```

O aplicativo empacotado está em `packages/desktop/out/`.
