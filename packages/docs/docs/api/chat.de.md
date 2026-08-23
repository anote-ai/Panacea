# Chat API

Basis-Pfad: `/api/chat`

## Stream Chat (SSE)

```http
POST /api/chat/stream
Authorization: Bearer <token>
Content-Type: application/json

{
  "message": "Erkläre diesen Codebestand",
  "model": "claude-sonnet-4-6",
  "session_id": null
}
```

Gibt einen Stream von Server-Sent Events zurück:

```
event: text
data: {"text": "Dieser Codebestand..."}

event: session_id
data: {"session_id": "abc123"}

event: done
data: {}
```

## Sitzungen auflisten

```http
GET /api/chat/sessions
Authorization: Bearer <token>
```

## Sitzungsnachrichten abrufen

```http
GET /api/chat/sessions/{id}
Authorization: Bearer <token>
```

## Sitzung löschen

```http
DELETE /api/chat/sessions/{id}
Authorization: Bearer <token>
```
