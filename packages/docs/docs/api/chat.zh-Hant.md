# 聊天 API

基本路徑: `/api/chat`

## 串流聊天 (SSE)

```http
POST /api/chat/stream
Authorization: Bearer <token>
Content-Type: application/json

{
  "message": "解釋這個程式碼庫",
  "model": "claude-sonnet-4-6",
  "session_id": null
}
```

返回伺服器推送事件串流：

```
event: text
data: {"text": "這個程式碼庫..."}

event: session_id
data: {"session_id": "abc123"}

event: done
data: {}
```

## 列出工作階段

```http
GET /api/chat/sessions
Authorization: Bearer <token>
```

## 獲取工作階段消息

```http
GET /api/chat/sessions/{id}
Authorization: Bearer <token>
```

## 刪除工作階段

```http
DELETE /api/chat/sessions/{id}
Authorization: Bearer <token>
```
