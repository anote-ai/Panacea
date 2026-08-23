# Panacea Abrechnung, API-Schlüssel & Kreditmessung

Dieses Rezept erklärt, wie Panacea die Nutzung misst, API-Aufrufer authentifiziert und Stripe-Abonnements in ein verfügbares Guthaben umwandelt.

## Was Sie lernen werden

- Die drei Möglichkeiten, wie eine Anfrage authentifiziert werden kann: JWT, Sitzungstoken oder langlebiger API-Schlüssel
- Wie Guthaben pro Anfrage überprüft und abgezogen werden und wie die Nutzung protokolliert wird
- Wie ein Stripe-Abonnement-Checkout zu einem aktualisierten Guthabenfluss führt
- Wie Benutzer ihre eigenen API-Schlüssel generieren, auflisten und widerrufen
- Die Missbrauchsschutzmaßnahmen, die neue/geänderte Abonnements steuern

## Warum das wichtig ist

Panacea ist nicht nur eine RAG-Demo — es ist ein gemessenes Produkt mit echten Abonnementstufen. Jeder Dokumenten-Upload, jede Chat-Vervollständigung oder Bewertungsanruf kostet Guthaben, und Guthaben werden durch ein aktives Stripe-Abonnement aufgefüllt. Dieses Rezept beschreibt den gesamten Ablauf: wie ein Aufrufer beweist, wer er ist, wie diese Identität bepreist wird und wie Geld (über Stripe) wieder in verwendbare Guthaben umgewandelt wird.

## Wichtige Panacea-Dateien

| Datei | Warum es wichtig ist |
|---|---|
| `Panacea/backend/database/db_auth.py` | `extractUserEmailFromRequest()` versucht JWT → Sitzungstoken → API-Schlüssel in dieser Reihenfolge; `user_has_credits()`, `api_key_user_has_credits()`, `deduct_credits_from_api_key_user()`; Missbrauchsschutzmaßnahmen in `verifyAuthForNewSubscriptipns()` |
| `Panacea/backend/database/usage.py` | `log_api_usage()` schreibt eine Zeile pro Anfrage in `api_usage`; `get_usage_summary()` / `get_usage_rows()` ermöglichen die Nutzungsauswertung |
| `Panacea/backend/api_endpoints/payments/handler.py` | `CreateCheckoutSessionHandler`, `CreatePortalSessionHandler`, `StripeWebhookHandler` |
| `Panacea/backend/api_endpoints/generate_api_key/handler.py`, `get_api_keys/handler.py`, `delete_api_key/handler.py`, `refresh_credits/handler.py` | API-Schlüssel erstellen, auflisten, widerrufen; Guthaben manuell auffrischen |
| `Panacea/backend/stripe_config/portal_config.py` | Konfiguration des Stripe Billing Portals pro Stufe |

## So funktioniert es

1. **Authentifizieren.** Jede geschützte Route ruft `extractUserEmailFromRequest(request)` auf, das den Header `Authorization: Bearer <token>` liest und versucht, in folgender Reihenfolge: als JWT dekodieren, als Sitzungstoken nachschlagen (`user_email_for_session_token`), dann als API-Schlüssel nachschlagen (`user_email_for_api_key`). Was auch immer zuerst erfolgreich ist, löst die E-Mail des Aufrufers auf.
2. **Guthaben überprüfen.** Bevor eine Anfrage bedient wird, ruft das Backend `user_has_credits(user_email)` (JWT/Sitzungsaufrufer) oder `api_key_user_has_credits(api_key)` (API-Schlüsselaufrufer) auf, um zu bestätigen, dass die `credits`-Spalte des Benutzers in `users` mindestens 1 beträgt.
3. **Abziehen und protokollieren.** Nach Abschluss verringert `deduct_credits_from_api_key_user()` das Guthaben und `log_api_usage()` fügt eine Zeile in `api_usage` mit dem Endpunkt, Modell, Token-Anzahlen und ausgegebenen Guthaben ein — dies ist es, was `GET /v1/usage` und `GET /v1/account` antreibt.
4. **Upgrade über Stripe.** Das Frontend ruft `POST /createCheckoutSession` auf, was `CreateCheckoutSessionHandler` erreicht: es löst den Benutzer auf, mappt den angeforderten `product_hash` auf eine Stripe-Preis-ID und erstellt eine `stripe.checkout.Session` im `subscription`-Modus (optional mit einem 30-tägigen kostenlosen Testcode).
5. **Webhook schließt den Kreis.** Stripe ruft `POST /stripeWebhook` bei `checkout.session.completed` zurück; `StripeWebhookHandler` protokolliert das neue Abonnement über `add_subscription()` und ruft `refresh_credits(user_email)` auf, um das Guthaben des Benutzers aufzufrischen. `customer.subscription.updated` (Stornierung) und `.deleted`-Ereignisse werden symmetrisch behandelt.
6. **Abonnement verwalten.** `POST /createPortalSession` (`CreatePortalSessionHandler`) öffnet eine Stripe Billing Portal-Sitzung, die auf die aktuelle Stufe des Benutzers über `config_for_payment_tiers()` beschränkt ist, sodass Upgrades/Downgrades/Stornierungen über die gehostete UI von Stripe erfolgen.
7. **API-Schlüssel.** `POST /generateAPIKey` erfordert mindestens 1 Guthaben und ruft `generate_api_key()` auf; `GET /getAPIKeys` und `POST /deleteAPIKey` listen/widerrufen Schlüssel auf, die jeweils mit einem `last_used` Zeitstempel verfolgt werden (`touch_api_key_last_used`).

### Missbrauchsschutzmaßnahmen

`verifyAuthForNewSubscriptipns()` in `db_auth.py` begrenzt neue Abonnements pro Stufe pro Tag (z.B. 25/Tag für Premium, 5/Tag für Enterprise), sendet eine interne Warnung bei definierten Schwellenwerten (5, 10, 50, 100, 200, 500 neue Abonnements/Tag) und blockiert einen Benutzer daran, den Plan mehr als einmal in einem rollierenden Monat zu ändern.

## Lokal ausführen

Vom Arbeitsbereichs-Stammverzeichnis (`anote/panacea`):

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

Setzen Sie diese in `backend/.env`, um den Abrechnungsfluss zu testen:

```bash
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
FRONTEND_URL=http://localhost:3000
JWT_SECRET_KEY=some-dev-secret
```

Leiten Sie Stripe-Webhooks an Ihr lokales Backend mit dem Stripe CLI weiter:

```bash
stripe listen --forward-to localhost:5000/stripeWebhook
```

### Probieren Sie es aus

```bash
# Generieren Sie einen API-Schlüssel (erfordert ein authentifiziertes JWT/Sitzung und >=1 Guthaben)
curl -X POST http://localhost:5000/generateAPIKey \
  -H "Authorization: Bearer <jwt_or_session_token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "mein erster Schlüssel"}'

# Überprüfen Sie die Nutzung mit dem neuen API-Schlüssel
curl http://localhost:5000/v1/usage \
  -H "Authorization: Bearer <api_key>"
```

## Hinweise für das Kochbuch

Kombinieren Sie dies mit Rezept 07 (OpenAI-kompatibles API-Gateway) — die hier generierten API-Schlüssel sind es, die `AnoteOpenAI`-Aufrufe authentifizieren. Es ist erwähnenswert, dass der Tippfehler `verifyAuthForNewSubscriptipns` im Funktionsnamen eine bekannte Eigenheit ist, falls ein Leser danach im Code sucht.
