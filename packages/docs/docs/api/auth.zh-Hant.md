# 認證 API

基本路徑: `/auth`

## 註冊

```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "name": "Alice"
}
```

**回應**
```json
{ "access_token": "eyJ..." }
```

## 登入

```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

## 刷新權杖

```http
POST /auth/refresh
Authorization: Bearer <token>
```

## 獲取當前用戶

```http
GET /auth/me
Authorization: Bearer <token>
```

**回應**
```json
{
  "id": "1",
  "email": "user@example.com",
  "name": "Alice"
}
```
