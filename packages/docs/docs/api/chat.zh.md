# 聊天 API

基础路径: `/api/chat`

## 流式聊天 (SSE)

```http
POST /api/chat/stream
Authorization: Bearer <token>
Content-Type: application/json

{
  "message": "解释这个代码库",
  "model": "claude-sonnet-4-6",
  "session_id": null
}
```

返回一个服务器推送事件流：

```
event: text
data: {"text": "这个代码库..."}

event: session_id
data: {"session_id": "abc123"}

event: done
data: {}
```

## 列出会话

```http
GET /api/chat/sessions
Authorization: Bearer <token>
```

## 获取会话消息

```http
GET /api/chat/sessions/{id}
Authorization: Bearer <token>
```

## 删除会话

```http
DELETE /api/chat/sessions/{id}
Authorization: Bearer <token>
```
