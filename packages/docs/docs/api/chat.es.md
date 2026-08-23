# API de Chat

Ruta base: `/api/chat`

## Chat en Streaming (SSE)

```http
POST /api/chat/stream
Authorization: Bearer <token>
Content-Type: application/json

{
  "message": "Explica esta base de código",
  "model": "claude-sonnet-4-6",
  "session_id": null
}
```

Devuelve un flujo de Eventos Enviados por el Servidor:

```
event: text
data: {"text": "Esta base de código..."}

event: session_id
data: {"session_id": "abc123"}

event: done
data: {}
```

## Listar Sesiones

```http
GET /api/chat/sessions
Authorization: Bearer <token>
```

## Obtener Mensajes de la Sesión

```http
GET /api/chat/sessions/{id}
Authorization: Bearer <token>
```

## Eliminar Sesión

```http
DELETE /api/chat/sessions/{id}
Authorization: Bearer <token>
```
