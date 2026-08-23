# TypeScript SDK

`@anote-ai/sdk` — это типизированный клиент TypeScript/JavaScript для Anote REST API. Используйте его, когда хотите вызывать Anote программно — из скрипта, бэкенд-сервиса или вашего собственного приложения — вместо того, чтобы использовать CLI или веб-приложение.

!!! note "Общение с локальным бэкендом"
    По умолчанию клиент указывает на `https://api.anote.ai`. Если вы запускаете бэкенд из этого репозитория локально (`docker compose up` или `make dev-backend`), передайте `baseUrl: "http://localhost:5050"` (или `:5000`, если вы не используете переопределение порта) — смотрите [Начало работы → Конфигурация](../getting-started/configuration.md).

## Что вам понадобится

- Node.js 18+
- Учетная запись Anote (зарегистрируйтесь через `POST /auth/register` или страницу регистрации веб-приложения)
- API-ключ (Шаг 2 ниже)

## 1. Установка

```bash
npm install @anote-ai/sdk
```

## 2. Получите API-ключ

Пока нет пользовательского интерфейса настроек для API-ключей, поэтому создайте один напрямую через бэкенд. Сначала войдите, чтобы получить JWT, затем используйте его для создания ключа:

```bash
# Войдите, чтобы получить JWT
curl -X POST http://localhost:5050/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "you@example.com", "password": "..."}'
# → { "access_token": "eyJ..." }

# Используйте JWT для создания API-ключа
curl -X POST http://localhost:5050/api/user/api-keys \
  -H "Authorization: Bearer eyJ..."
# → { "key": "ak-..." }
```

Сохраните это значение `ak-...` — оно возвращается только один раз, во время создания.

## 3. Инициализация клиента

```ts
import { AnoteClient } from "@anote-ai/sdk";

const client = new AnoteClient({
  apiKey: "ak-...",
  baseUrl: "http://localhost:5050", // опустите, чтобы использовать https://api.anote.ai
});
```

`apiKey` — это единственный обязательный параметр. Оставьте `baseUrl` пустым, когда вы находитесь на производственном API.

## 4. Отправьте ваше первое сообщение

```ts
const { result, usage } = await client.chat("Объясните эту кодовую базу");

console.log(result);
console.log(`Использовано ${usage.inputTokens} входных / ${usage.outputTokens} выходных токенов`);
```

`chat()` — это вызов без потоковой передачи — он ждет полного ответа, что вам нужно для скриптов и автоматизации. Передайте `cwd`, `model` или `tools` во втором аргументе, чтобы задать рабочую директорию, выбрать модель или ограничить, какие инструменты может использовать ИИ:

```ts
await client.chat("Перечислите TODO в этом файле", {
  cwd: "/path/to/project",
  model: "claude-sonnet-4-6",
  tools: ["Read", "Grep"],
});
```

## Общие задачи

**Перечислите и проверьте прошлые сессии**

```ts
const sessions = await client.listSessions();
const { history } = await client.getSessionMessages(sessions[0].sessionId);
```

**Поиск по истории сессий**

```ts
const { results } = await client.search("логика аутентификации");
```

**Проверьте ваше использование и квоту**

```ts
const usage = await client.getUsage();
console.log(`${usage.remaining.requests} запросов осталось в этом месяце`);
```

**Поделитесь сессией в виде ссылки только для чтения**

```ts
const { shareUrl } = await client.shareSession(sessions[0].sessionId);
```

**Обработка ошибок**

Каждый ответ, не относящийся к 2xx, вызывает `AnoteError`, который содержит HTTP-статус и разобранное тело ответа:

```ts
import { AnoteClient, AnoteError } from "@anote-ai/sdk";

try {
  await client.chat("...");
} catch (err) {
  if (err instanceof AnoteError) {
    console.error(err.status, err.message); // например, 429, "Превышена месячная квота"
  }
}
```

**Проверьте работоспособность сервера (авторизация не требуется)**

```ts
const health = await client.health();
```

## Справочник API

### `new AnoteClient(options)`

| Параметр | Тип | Обязательный | Описание |
|---|---|---|---|
| `apiKey` | `string` | ✓ | API-ключ из Шага 2, начинается с `ak-` |
| `baseUrl` | `string` | | URL сервера (по умолчанию: `https://api.anote.ai`) |

### Методы

| Метод | Описание |
|--------|-------------|
| `chat(message, options?)` | Отправить сообщение, получить полный ответ ИИ |
| `listSessions()` | Перечислить все сессии чата |
| `getSessionMessages(id)` | Получить историю сообщений для сессии |
| `deleteSession(id)` | Удалить сессию |
| `shareSession(id)` | Создать ссылку только для чтения |
| `search(query, limit?)` | Полнотекстовый поиск по сессиям |
| `getUsage()` | Использование текущего месяца + квота |
| `health()` | Проверка работоспособности сервера (авторизация не нужна) |

## Следующие шаги

- [Обзор API бэкенда](../api/overview.md) — REST-эндпоинты, лежащие в основе этого SDK
- [Обзор CLI](../cli/overview.md) — для интерактивного/терминального использования вместо скриптов
