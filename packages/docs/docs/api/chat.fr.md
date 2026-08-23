# API de Chat

Chemin de base : `/api/chat`

## Chat en Flux (SSE)

```http
POST /api/chat/stream
Authorization: Bearer <token>
Content-Type: application/json

{
  "message": "Expliquez cette base de code",
  "model": "claude-sonnet-4-6",
  "session_id": null
}
```

Renvoie un flux d'événements envoyés par le serveur :

```
event: text
data: {"text": "Cette base de code..."}

event: session_id
data: {"session_id": "abc123"}

event: done
data: {}
```

## Lister les Sessions

```http
GET /api/chat/sessions
Authorization: Bearer <token>
```

## Obtenir les Messages de la Session

```http
GET /api/chat/sessions/{id}
Authorization: Bearer <token>
```

## Supprimer la Session

```http
DELETE /api/chat/sessions/{id}
Authorization: Bearer <token>
```
