# 채팅 API

기본 경로: `/api/chat`

## 스트림 채팅 (SSE)

```http
POST /api/chat/stream
Authorization: Bearer <token>
Content-Type: application/json

{
  "message": "이 코드베이스를 설명해 주세요",
  "model": "claude-sonnet-4-6",
  "session_id": null
}
```

서버 전송 이벤트 스트림을 반환합니다:

```
event: text
data: {"text": "이 코드베이스..."}

event: session_id
data: {"session_id": "abc123"}

event: done
data: {}
```

## 세션 목록

```http
GET /api/chat/sessions
Authorization: Bearer <token>
```

## 세션 메시지 가져오기

```http
GET /api/chat/sessions/{id}
Authorization: Bearer <token>
```

## 세션 삭제

```http
DELETE /api/chat/sessions/{id}
Authorization: Bearer <token>
```
