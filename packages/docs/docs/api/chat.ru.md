# Chat API

Базовый путь: `/api/chat`

## Stream Chat (SSE)

```http
POST /api/chat/stream
Authorization: Bearer <token>
Content-Type: application/json

{
  "message": "Объясните эту кодовую базу",
  "model": "claude-sonnet-4-6",
  "session_id": null
}
```

Возвращает поток событий, отправляемых сервером:

```
event: text
data: {"text": "Эта кодовая база..."}

event: session_id
data: {"session_id": "abc123"}

event: done
data: {}
```

## Список сессий

```http
GET /api/chat/sessions
Authorization: Bearer <token>
```

## Получить сообщения сессии

```http
GET /api/chat/sessions/{id}
Authorization: Bearer <token>
```

## Удалить сессию

```http
DELETE /api/chat/sessions/{id}
Authorization: Bearer <token>
```
