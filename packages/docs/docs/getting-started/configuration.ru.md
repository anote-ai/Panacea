# Конфигурация

## Конфигурация CLI

Конфигурация хранится в `~/.anote/config.json`:

```json
{
  "model": "claude-sonnet-4-6",
  "provider": "anthropic",
  "apiKey": "sk-ant-...",
  "serverUrl": "http://localhost:5000",
  "maxTurns": 30,
  "permissionMode": "default"
}
```

Управление через:

```bash
anote config set model claude-opus-4-8
anote config get model
anote config list
```

## Переменные окружения

Все настройки могут быть переопределены с помощью переменных окружения:

| Переменная | Назначение |
|---|---|
| `ANTHROPIC_API_KEY` | Ключ API Anthropic |
| `OPENAI_API_KEY` | Ключ API OpenAI |
| `GEMINI_API_KEY` | Ключ API Google Gemini |
| `ANOTE_MODEL` | Модель по умолчанию |
| `ANOTE_SERVER_URL` | URL бэкенда Anote |

## Конфигурация бэкенда

Скопируйте `packages/backend/.env.example` в `packages/backend/.env` и заполните:

```bash
# Поставщики LLM
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...

# База данных
DB_HOST=localhost
DB_NAME=anote
DB_USER=anote
DB_PASSWORD=anote

# Аутентификация
JWT_SECRET_KEY=your-secret-key

# Платежи (по желанию)
STRIPE_SECRET_KEY=sk_...
```
