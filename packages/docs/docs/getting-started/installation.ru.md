# Установка

## CLI

```bash
npm install -g @anote-ai/anote
```

Требуется Node.js 18 или более поздняя версия.

## Расширение для VS Code

Ищите **"Anote"** в маркетплейсе расширений VS Code или установите через:

```bash
code --install-extension anote-ai.anote-ai-coding
```

## Веб-приложение (самостоятельный хостинг)

```bash
git clone https://github.com/anote-ai/Panacea
cd Panacea
cp packages/backend/.env.example packages/backend/.env
# Отредактируйте .env с вашими API ключами
docker compose up
```

Фронтенд: http://localhost:3000 · Бэкенд: http://localhost:5000

## Десктопное приложение

Скачайте последнюю версию с [GitHub Releases](https://github.com/anote-ai/Panacea/releases).

Доступно для: **macOS** (DMG), **Windows** (установщик), **Linux** (AppImage/DEB/RPM).

## Python SDK

```bash
pip install anote-ai
```

## TypeScript/JavaScript SDK

```bash
npm install @anote-ai/sdk
```
