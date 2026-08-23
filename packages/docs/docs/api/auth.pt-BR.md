# API de Autenticação

Caminho base: `/auth`

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

**Resposta**
```json
{ "access_token": "eyJ..." }
```

## Login

```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

## Atualizar Token

```http
POST /auth/refresh
Authorization: Bearer <token>
```

## Obter Usuário Atual

```http
GET /auth/me
Authorization: Bearer <token>
```

**Resposta**
```json
{
  "id": "1",
  "email": "user@example.com",
  "name": "Alice"
}
```
