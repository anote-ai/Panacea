# Aperçu de l'API Backend

Le backend d'Anote est une API Flask unifiée servant toutes les surfaces client.

URL de base : `http://localhost:5000` (local) ou l'URL de votre backend déployé.

## Authentification

Tous les points de terminaison protégés nécessitent un jeton JWT :

```
Authorization: Bearer <token>
```

Obtenez un jeton via `POST /auth/login` ou `POST /auth/register`.

## Points de terminaison clés

### Agent Chat (Streaming)

```
POST /api/chat/stream          # Chat en streaming SSE
POST /api/chat                 # Chat non-streaming
GET  /api/chat/sessions        # Lister les sessions
POST /api/chat/sessions        # Créer une session
```

### Documents

```
POST /api/documents/upload     # Télécharger un document
GET  /api/documents            # Lister les documents
GET  /api/documents/{id}       # Obtenir un document
DELETE /api/documents/{id}     # Supprimer un document
POST /api/documents/{id}/ask   # Q&R sur le document
```

### Recherche sémantique

```
GET  /api/search?q=...&cwd=... # Rechercher dans le code indexé
```

### Authentification

```
POST /auth/register            # S'inscrire
POST /auth/login               # Se connecter
POST /auth/refresh             # Rafraîchir le JWT
GET  /auth/google              # OAuth Google
```

### Utilisateur & Facturation

```
GET  /api/user/profile         # Obtenir l'utilisateur
POST /api/payments/checkout    # Paiement Stripe
POST /api/payments/portal      # Portail client
POST /api/payments/webhook     # Webhook Stripe
```
