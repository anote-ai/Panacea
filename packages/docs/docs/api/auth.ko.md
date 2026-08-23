# 인증 API

기본 경로: `/auth`

## 등록

```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "name": "Alice"
}
```

**응답**
```json
{ "access_token": "eyJ..." }
```

## 로그인

```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

## 토큰 갱신

```http
POST /auth/refresh
Authorization: Bearer <token>
```

## 현재 사용자 가져오기

```http
GET /auth/me
Authorization: Bearer <token>
```

**응답**
```json
{
  "id": "1",
  "email": "user@example.com",
  "name": "Alice"
}
```
