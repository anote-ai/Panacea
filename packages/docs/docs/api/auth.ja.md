# 認証 API

ベースパス: `/auth`

## 登録

```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "name": "Alice"
}
```

**レスポンス**
```json
{ "access_token": "eyJ..." }
```

## ログイン

```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

## トークンの更新

```http
POST /auth/refresh
Authorization: Bearer <token>
```

## 現在のユーザーを取得

```http
GET /auth/me
Authorization: Bearer <token>
```

**レスポンス**
```json
{
  "id": "1",
  "email": "user@example.com",
  "name": "Alice"
}
```
