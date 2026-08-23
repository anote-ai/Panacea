# API аутентификации

Базовый путь: `/auth`

## Регистрация

```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "name": "Alice"
}
```

**Ответ**
```json
{ "access_token": "eyJ..." }
```

## Вход

```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

## Обновить токен

```http
POST /auth/refresh
Authorization: Bearer <token>
```

## Получить текущего пользователя

```http
GET /auth/me
Authorization: Bearer <token>
```

**Ответ**
```json
{
  "id": "1",
  "email": "user@example.com",
  "name": "Alice"
}
```
