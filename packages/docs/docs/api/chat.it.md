# Chat API

Percorso base: `/api/chat`

## Stream Chat (SSE)

```http
POST /api/chat/stream
Authorization: Bearer <token>
Content-Type: application/json

{
  "message": "Spiega questo codice sorgente",
  "model": "claude-sonnet-4-6",
  "session_id": null
}
```

Restituisce uno stream di eventi inviati dal server:

```
event: text
data: {"text": "Questo codice sorgente..."}

event: session_id
data: {"session_id": "abc123"}

event: done
data: {}
```

## Elenca Sessioni

```http
GET /api/chat/sessions
Authorization: Bearer <token>
```

## Ottieni Messaggi della Sessione

```http
GET /api/chat/sessions/{id}
Authorization: Bearer <token>
```

## Elimina Sessione

```http
DELETE /api/chat/sessions/{id}
Authorization: Bearer <token>
```
