# Panacea Fatturazione, Chiavi API e Misurazione del Credito

Questa ricetta spiega come Panacea misura l'uso, autentica i chiamanti API e trasforma gli abbonamenti Stripe in un saldo di credito spendibile.

## Cosa imparerai

- I tre modi in cui una richiesta può autenticarsi: JWT, token di sessione o chiave API a lungo termine
- Come i crediti vengono controllati e dedotti per richiesta, e come l'uso viene registrato
- Come un checkout di abbonamento Stripe fluisce verso un saldo di credito aggiornato
- Come gli utenti generano, elencano e revocano le proprie chiavi API
- Le protezioni contro gli abusi che regolano nuovi/variati abbonamenti

## Perché è importante

Panacea non è solo una demo RAG — è un prodotto misurato con veri livelli di abbonamento. Ogni caricamento di documento, completamento di chat o chiamata di valutazione costa crediti, e i crediti vengono ripristinati da un abbonamento Stripe attivo. Questa ricetta attraversa l'intero ciclo: come un chiamante prova chi è, come quella identità viene valutata e come il denaro (tramite Stripe) si trasforma di nuovo in crediti utilizzabili.

## File chiave di Panacea

| File | Perché è importante |
|---|---|
| `Panacea/backend/database/db_auth.py` | `extractUserEmailFromRequest()` prova JWT → token di sessione → chiave API in sequenza; `user_has_credits()`, `api_key_user_has_credits()`, `deduct_credits_from_api_key_user()`; protezioni contro gli abusi in `verifyAuthForNewSubscriptipns()` |
| `Panacea/backend/database/usage.py` | `log_api_usage()` scrive una riga per richiesta in `api_usage`; `get_usage_summary()` / `get_usage_rows()` alimentano la reportistica dell'uso |
| `Panacea/backend/api_endpoints/payments/handler.py` | `CreateCheckoutSessionHandler`, `CreatePortalSessionHandler`, `StripeWebhookHandler` |
| `Panacea/backend/api_endpoints/generate_api_key/handler.py`, `get_api_keys/handler.py`, `delete_api_key/handler.py`, `refresh_credits/handler.py` | Genera, elenca, revoca chiavi API; aggiorna manualmente i crediti |
| `Panacea/backend/stripe_config/portal_config.py` | Configurazione del Portale di Fatturazione Stripe per livello |

## Come funziona

1. **Autenticazione.** Ogni percorso protetto chiama `extractUserEmailFromRequest(request)`, che legge l'intestazione `Authorization: Bearer <token>` e prova, in ordine: decodificare come JWT, cercare come token di sessione (`user_email_for_session_token`), quindi cercare come chiave API (`user_email_for_api_key`). Quello che riesce per primo risolve l'email del chiamante.
2. **Controlla i crediti.** Prima di servire una richiesta, il backend chiama `user_has_credits(user_email)` (chiamanti JWT/sessione) o `api_key_user_has_credits(api_key)` (chiamanti chiave API) per confermare che la colonna `credits` dell'utente in `users` sia almeno 1.
3. **Deduzione e registrazione.** Al termine, `deduct_credits_from_api_key_user()` decrementa il saldo e `log_api_usage()` inserisce una riga in `api_usage` con l'endpoint, il modello, i conteggi dei token e i crediti spesi — questo alimenta `GET /v1/usage` e `GET /v1/account`.
4. **Aggiornamento tramite Stripe.** Il frontend chiama `POST /createCheckoutSession`, che colpisce `CreateCheckoutSessionHandler`: risolve l'utente, mappa il `product_hash` richiesto a un ID prezzo Stripe e crea una `stripe.checkout.Session` in modalità `subscription` (applicando facoltativamente un codice di prova gratuito di 30 giorni).
5. **Webhook completa il ciclo.** Stripe richiama `POST /stripeWebhook` su `checkout.session.completed`; `StripeWebhookHandler` registra il nuovo abbonamento tramite `add_subscription()` e chiama `refresh_credits(user_email)` per ricaricare il saldo dell'utente. Gli eventi `customer.subscription.updated` (cancellazione) e `.deleted` vengono gestiti simmetricamente.
6. **Gestisci l'abbonamento.** `POST /createPortalSession` (`CreatePortalSessionHandler`) apre una sessione del Portale di Fatturazione Stripe limitata al livello attuale dell'utente tramite `config_for_payment_tiers()`, quindi gli aggiornamenti/declassamenti/cancellazioni avvengono attraverso l'interfaccia ospitata di Stripe.
7. **Chiavi API.** `POST /generateAPIKey` richiede almeno 1 credito e chiama `generate_api_key()`; `GET /getAPIKeys` e `POST /deleteAPIKey` elencano/revocano chiavi, ciascuna tracciata con un timestamp `last_used` (`touch_api_key_last_used`).

### Protezioni contro gli abusi

`verifyAuthForNewSubscriptipns()` in `db_auth.py` limita i nuovi abbonamenti per livello al giorno (ad esempio, 25/giorno per Premium, 5/giorno per Enterprise), invia un avviso interno via email a soglie definite (5, 10, 50, 100, 200, 500 nuovi abbonamenti/giorno) e blocca un utente dal cambiare piano più di una volta in un mese mobile.

## Esegui localmente

Dalla radice del workspace (`anote/panacea`):

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

Imposta questi in `backend/.env` per esercitare il flusso di fatturazione:

```bash
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
FRONTEND_URL=http://localhost:3000
JWT_SECRET_KEY=some-dev-secret
```

Inoltra i webhook di Stripe al tuo backend locale con Stripe CLI:

```bash
stripe listen --forward-to localhost:5000/stripeWebhook
```

### Provalo

```bash
# Genera una chiave API (richiede un JWT/sessione autenticata, e >=1 credito)
curl -X POST http://localhost:5000/generateAPIKey \
  -H "Authorization: Bearer <jwt_or_session_token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "la mia prima chiave"}'

# Controlla l'uso con la nuova chiave API
curl http://localhost:5000/v1/usage \
  -H "Authorization: Bearer <api_key>"
```

## Note per il ricettario

Abbina questo con la ricetta 07 (Gateway API compatibile con OpenAI) — le stesse chiavi API generate qui sono quelle che autenticano le chiamate a `AnoteOpenAI`. Vale la pena segnalare il refuso `verifyAuthForNewSubscriptipns` nel nome della funzione come una stranezza nota se un lettore va a cercarlo nel codice.
