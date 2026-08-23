# API d'Authentification

Chemin de base : `/auth`

## Inscription

```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "name": "Alice"
}
```

**Réponse**
```json
{ "access_token": "eyJ..." }
```

## Connexion

```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

## Rafraîchir le Jeton

```http
POST /auth/refresh
Authorization: Bearer <token>
```

## Obtenir l'Utilisateur Actuel

```http
GET /auth/me
Authorization: Bearer <token>
```

**Réponse**
```json
{
  "id": "1",
  "email": "user@example.com",
  "name": "Alice"
}
```
