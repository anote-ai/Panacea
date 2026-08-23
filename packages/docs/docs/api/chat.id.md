# API Obrolan

Jalur dasar: `/api/chat`

## Obrolan Streaming (SSE)

```http
POST /api/chat/stream
Authorization: Bearer <token>
Content-Type: application/json

{
  "message": "Jelaskan kode basis ini",
  "model": "claude-sonnet-4-6",
  "session_id": null
}
```

Mengembalikan aliran Server-Sent Events:

```
event: text
data: {"text": "Kode basis ini..."}

event: session_id
data: {"session_id": "abc123"}

event: done
data: {}
```

## Daftar Sesi

```http
GET /api/chat/sessions
Authorization: Bearer <token>
```

## Dapatkan Pesan Sesi

```http
GET /api/chat/sessions/{id}
Authorization: Bearer <token>
```

## Hapus Sesi

```http
DELETE /api/chat/sessions/{id}
Authorization: Bearer <token>
```
