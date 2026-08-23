# チャット API

基本パス: `/api/chat`

## ストリームチャット (SSE)

```http
POST /api/chat/stream
Authorization: Bearer <token>
Content-Type: application/json

{
  "message": "このコードベースを説明してください",
  "model": "claude-sonnet-4-6",
  "session_id": null
}
```

サーバー送信イベントストリームを返します:

```
event: text
data: {"text": "このコードベース..."}

event: session_id
data: {"session_id": "abc123"}

event: done
data: {}
```

## セッションの一覧

```http
GET /api/chat/sessions
Authorization: Bearer <token>
```

## セッションメッセージの取得

```http
GET /api/chat/sessions/{id}
Authorization: Bearer <token>
```

## セッションの削除

```http
DELETE /api/chat/sessions/{id}
Authorization: Bearer <token>
```
