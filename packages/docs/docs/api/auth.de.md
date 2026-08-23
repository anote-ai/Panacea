# Authentifizierungs-API

Basis-Pfad: `/auth`

## Registrierung

```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "name": "Alice"
}
```

**Antwort**
```json
{ "access_token": "eyJ..." }
```

## Anmeldung

```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

## Token erneuern

```http
POST /auth/refresh
Authorization: Bearer <token>
```

## Aktuellen Benutzer abrufen

```http
GET /auth/me
Authorization: Bearer <token>
```

**Antwort**
```json
{
  "id": "1",
  "email": "user@example.com",
  "name": "Alice"
}
```
