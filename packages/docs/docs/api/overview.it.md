# Panoramica dell'API Backend

Il backend di Anote è un'API Flask unificata che serve tutte le superfici client.

URL di base: `http://localhost:5000` (locale) o l'URL del tuo backend distribuito.

## Autenticazione

Tutti gli endpoint protetti richiedono un token JWT:

```
Authorization: Bearer <token>
```

Ottieni un token tramite `POST /auth/login` o `POST /auth/register`.

## Endpoint Chiave

### Chat Agente (Streaming)

```
POST /api/chat/stream          # Chat in streaming SSE
POST /api/chat                 # Chat non in streaming
GET  /api/chat/sessions        # Elenco delle sessioni
POST /api/chat/sessions        # Crea sessione
```

### Documenti

```
POST /api/documents/upload     # Carica documento
GET  /api/documents            # Elenco documenti
GET  /api/documents/{id}       # Ottieni documento
DELETE /api/documents/{id}     # Elimina documento
POST /api/documents/{id}/ask   # Q&A sul documento
```

### Ricerca Semantica

```
GET  /api/search?q=...&cwd=... # Cerca nel codice indicizzato
```

### Autenticazione

```
POST /auth/register            # Registrati
POST /auth/login               # Accedi
POST /auth/refresh             # Aggiorna JWT
GET  /auth/google              # Google OAuth
```

### Utente & Fatturazione

```
GET  /api/user/profile         # Ottieni utente
POST /api/payments/checkout    # Checkout Stripe
POST /api/payments/portal      # Portale cliente
POST /api/payments/webhook     # Webhook Stripe
```
