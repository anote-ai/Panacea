# API de Chat

Caminho base: `/api/chat`

## Chat em Stream (SSE)

```http
POST /api/chat/stream
Authorization: Bearer <token>
Content-Type: application/json

{
  "message": "Explique este código",
  "model": "claude-sonnet-4-6",
  "session_id": null
}
```

Retorna um stream de Eventos Enviados pelo Servidor:

```
event: text
data: {"text": "Este código..."}

event: session_id
data: {"session_id": "abc123"}

event: done
data: {}
```

## Listar Sessões

```http
GET /api/chat/sessions
Authorization: Bearer <token>
```

## Obter Mensagens da Sessão

```http
GET /api/chat/sessions/{id}
Authorization: Bearer <token>
```

## Deletar Sessão

```http
DELETE /api/chat/sessions/{id}
Authorization: Bearer <token>
```
