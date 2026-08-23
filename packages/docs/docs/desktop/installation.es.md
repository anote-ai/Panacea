# Instalación de la Aplicación de Escritorio

## Descarga

Descarga la última versión para tu plataforma desde la página de lanzamientos de GitHub.

| Plataforma | Archivo |
|------------|---------|
| macOS      | `Anote-AI-x.x.x.dmg` |
| Windows    | `Anote-AI-Setup-x.x.x.exe` |
| Linux (deb)| `anote-ai_x.x.x_amd64.deb` |

## Compilación desde el Código Fuente

```bash
# 1. Agrupar el backend de Python
cd packages/backend
pip install pyinstaller
pyinstaller ../desktop/app.spec --distpath ../desktop/backend-dist

# 2. Construir y empaquetar la aplicación de Electron
cd packages/desktop
npm install
npm run make
```

La aplicación empaquetada se encuentra en `packages/desktop/out/`.
