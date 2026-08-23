# Backend API Übersicht

Das Anote-Backend ist eine einheitliche Flask-API, die alle Client-Oberflächen bedient.

Basis-URL: `http://localhost:5000` (lokal) oder Ihre bereitgestellte Backend-URL.

## Authentifizierung

Alle geschützten Endpunkte erfordern ein JWT-Token:

```
Authorization: Bearer <token>
```

Erhalten Sie ein Token über `POST /auth/login` oder `POST /auth/register`.

## Wichtige Endpunkte

### Agent Chat (Streaming)

```
POST /api/chat/stream          # SSE Streaming-Chat
POST /api/chat                 # Nicht-Streaming-Chat
GET  /api/chat/sessions        # Sitzungen auflisten
POST /api/chat/sessions        # Sitzung erstellen
```

### Dokumente

```
POST /api/documents/upload     # Dokument hochladen
GET  /api/documents            # Dokumente auflisten
GET  /api/documents/{id}       # Dokument abrufen
DELETE /api/documents/{id}     # Dokument löschen
POST /api/documents/{id}/ask   # Q&A zum Dokument
```

### Semantische Suche

```
GET  /api/search?q=...&cwd=... # Durchsuchen des indizierten Codebestands
```

### Authentifizierung

```
POST /auth/register            # Registrieren
POST /auth/login               # Anmelden
POST /auth/refresh             # JWT aktualisieren
GET  /auth/google              # Google OAuth
```

### Benutzer & Abrechnung

```
GET  /api/user/profile         # Benutzer abrufen
POST /api/payments/checkout    # Stripe Checkout
POST /api/payments/portal      # Kundenportal
POST /api/payments/webhook     # Stripe Webhook
```
