# API Autentikasi

Path dasar: `/auth`

## Daftar

```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "name": "Alice"
}
```

**Respons**
```json
{ "access_token": "eyJ..." }
```

## Masuk

```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

## Segarkan Token

```http
POST /auth/refresh
Authorization: Bearer <token>
```

## Dapatkan Pengguna Saat Ini

```http
GET /auth/me
Authorization: Bearer <token>
```

**Respons**
```json
{
  "id": "1",
  "email": "user@example.com",
  "name": "Alice"
}
```
