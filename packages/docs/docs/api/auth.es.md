# API de Autenticación

Ruta base: `/auth`

## Registro

```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "name": "Alice"
}
```

**Respuesta**
```json
{ "access_token": "eyJ..." }
```

## Inicio de Sesión

```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

## Refrescar Token

```http
POST /auth/refresh
Authorization: Bearer <token>
```

## Obtener Usuario Actual

```http
GET /auth/me
Authorization: Bearer <token>
```

**Respuesta**
```json
{
  "id": "1",
  "email": "user@example.com",
  "name": "Alice"
}
```
