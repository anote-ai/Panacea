# Архитектура

## Структура Monorepo

```
Panacea/
├── packages/
│   ├── backend/    # Python Flask — унифицированный API + потоковая передача агента + RAG
│   ├── cli/        # TypeScript — терминал CLI anote
│   ├── vscode/     # TypeScript — расширение для VS Code
│   ├── web/        # TypeScript/React — веб-приложение чат-бота
│   ├── mobile/     # TypeScript/React Native (Expo) — iOS + Android
│   ├── desktop/    # TypeScript/Electron — частное настольное приложение
│   ├── sdk/        # TypeScript — JS/TS клиентский SDK
│   └── docs/       # MkDocs Material — сайт документации
├── docker-compose.yml
├── package.json    # npm workspaces
└── Makefile
```

## Архитектура бэкенда

Бэкенд на Python Flask обрабатывает всю серверную логику:

```
packages/backend/
├── app.py                    # Точка входа Flask, регистрация маршрутов
├── api_endpoints/
│   ├── chat/                 # Потоковая передача агента (SSE), управление сессиями
│   ├── documents/            # Загрузка, RAG конвейер, Вопросы и ответы
│   ├── search/               # Запросы к семантическому индексу поиска
│   ├── auth/                 # JWT, Google OAuth
│   ├── user/                 # Профиль, настройки
│   └── payments/             # Вебхуки Stripe + оформление заказа
├── agents/                   # Определения агентов LangChain/LangGraph
├── services/
│   ├── rag.py                # Разбиение документов + встраивания Chroma
│   ├── streaming.py          # SSE потоковая передача в Claude/OpenAI/Gemini
│   └── search.py             # Семантический поиск TF-IDF
├── database/
│   ├── db.py                 # Подключение к MySQL + запросы
│   └── schema.sql            # Схема базы данных
└── models/                   # Обертки для поставщиков LLM
```

## Поток данных: Чат агента

```
Клиент (CLI / VS Code / Веб / Мобильный)
    │  POST /api/chat/stream {message, cwd, model}
    ▼
Flask Бэкенд (app.py → chat/handler.py)
    │  SSE поток
    ▼
Поставщик LLM (Anthropic / OpenAI / Gemini / Ollama)
    │  вызовы инструментов ↔ выполнение (Чтение/Запись/Редактирование/Bash/Glob/Grep)
    ▼
Файловая система (cwd) + Chroma (контекст RAG)
```

## Выбор технологий

| Уровень | Технология | Почему |
|---|---|---|
| Бэкенд | Python Flask | Богатая экосистема ML/AI, существующие агенты |
| Потоковая передача агента | Anthropic Python SDK | Нативный SSE, использование инструментов |
| Векторная БД | ChromaDB | Локальный приоритет, не требуется инфраструктура |
| База данных | MySQL | ACID, существующая схема |
| Кэш | Redis | Управление сессиями + ограничение частоты |
| Фронтенд | React 18 + TypeScript | Безопасность типов, экосистема |
| Настольный | Electron | Кроссплатформенный, включает Python |
| Мобильный | Expo (React Native) | Совместное использование кода с вебом |
| CLI | Commander.js | Зрелый, удобный для TypeScript |
| Документация | MkDocs Material | Красивый, быстрый, markdown |
