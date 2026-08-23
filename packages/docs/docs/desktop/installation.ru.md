# Установка настольного приложения

## Загрузка

Скачайте последнюю версию для вашей платформы со страницы релизов GitHub.

| Платформа | Файл |
|-----------|------|
| macOS     | `Anote-AI-x.x.x.dmg` |
| Windows   | `Anote-AI-Setup-x.x.x.exe` |
| Linux (deb) | `anote-ai_x.x.x_amd64.deb` |

## Сборка из исходников

```bash
# 1. Упакуйте Python бэкенд
cd packages/backend
pip install pyinstaller
pyinstaller ../desktop/app.spec --distpath ../desktop/backend-dist

# 2. Соберите и упакуйте приложение Electron
cd packages/desktop
npm install
npm run make
```

Упакованное приложение находится в `packages/desktop/out/`.
