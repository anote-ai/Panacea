# 认证 API

基础路径: `/auth`

## 注册

```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "name": "Alice"
}
```

**响应**
```json
{ "access_token": "eyJ..." }
```

## 登录

```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

## 刷新令牌

```http
POST /auth/refresh
Authorization: Bearer <token>
```

## 获取当前用户

```http
GET /auth/me
Authorization: Bearer <token>
```

**响应**
```json
{
  "id": "1",
  "email": "user@example.com",
  "name": "Alice"
}
```
