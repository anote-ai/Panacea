# API di Autenticazione

Percorso base: `/auth`

## Registrazione

```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "name": "Alice"
}
```

**Risposta**
```json
{ "access_token": "eyJ..." }
```

## Accesso

```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

## Aggiorna Token

```http
POST /auth/refresh
Authorization: Bearer <token>
```

## Ottieni Utente Corrente

```http
GET /auth/me
Authorization: Bearer <token>
```

**Risposta**
```json
{
  "id": "1",
  "email": "user@example.com",
  "name": "Alice"
}
```
