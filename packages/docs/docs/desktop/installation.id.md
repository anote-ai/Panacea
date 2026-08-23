# Instalasi Aplikasi Desktop

## Unduh

Unduh rilis terbaru untuk platform Anda dari halaman rilis GitHub.

| Platform | File |
|----------|------|
| macOS | `Anote-AI-x.x.x.dmg` |
| Windows | `Anote-AI-Setup-x.x.x.exe` |
| Linux (deb) | `anote-ai_x.x.x_amd64.deb` |

## Membangun dari Sumber

```bash
# 1. Mengemas backend Python
cd packages/backend
pip install pyinstaller
pyinstaller ../desktop/app.spec --distpath ../desktop/backend-dist

# 2. Membangun dan mengemas aplikasi Electron
cd packages/desktop
npm install
npm run make
```

Aplikasi yang telah dikemas berada di `packages/desktop/out/`.
