# Panacea Facturación, Claves API y Medición de Créditos

Esta receta explica cómo Panacea mide el uso, autentica a los llamadores de la API y convierte las suscripciones de Stripe en un saldo de crédito gastable.

## Lo que aprenderás

- Las tres formas en que una solicitud puede autenticarse: JWT, token de sesión o clave API de larga duración
- Cómo se verifican y deducen los créditos por solicitud, y cómo se registra el uso
- Cómo un flujo de pago de suscripción de Stripe se traduce en un saldo de crédito actualizado
- Cómo los usuarios generan, listan y revocan sus propias claves API
- Las medidas de protección contra abusos que regulan nuevas suscripciones/cambios

## Por qué esto es importante

Panacea no es solo una demostración de RAG: es un producto medido con niveles de suscripción reales. Cada carga de documento, finalización de chat o llamada de evaluación cuesta créditos, y los créditos se reponen mediante una suscripción activa de Stripe. Esta receta recorre todo el ciclo: cómo un llamador prueba quién es, cómo se valora esa identidad y cómo el dinero (a través de Stripe) se convierte nuevamente en créditos utilizables.

## Archivos clave de Panacea

| Archivo | Por qué es importante |
|---|---|
| `Panacea/backend/database/db_auth.py` | `extractUserEmailFromRequest()` intenta JWT → token de sesión → clave API en secuencia; `user_has_credits()`, `api_key_user_has_credits()`, `deduct_credits_from_api_key_user()`; medidas de protección contra abusos en `verifyAuthForNewSubscriptipns()` |
| `Panacea/backend/database/usage.py` | `log_api_usage()` escribe una fila por solicitud en `api_usage`; `get_usage_summary()` / `get_usage_rows()` alimentan los informes de uso |
| `Panacea/backend/api_endpoints/payments/handler.py` | `CreateCheckoutSessionHandler`, `CreatePortalSessionHandler`, `StripeWebhookHandler` |
| `Panacea/backend/api_endpoints/generate_api_key/handler.py`, `get_api_keys/handler.py`, `delete_api_key/handler.py`, `refresh_credits/handler.py` | Crear, listar, revocar claves API; refrescar créditos manualmente |
| `Panacea/backend/stripe_config/portal_config.py` | Configuración del Portal de Facturación de Stripe por nivel |

## Cómo funciona

1. **Autenticación.** Cada ruta protegida llama a `extractUserEmailFromRequest(request)`, que lee el encabezado `Authorization: Bearer <token>` e intenta, en orden: decodificar como un JWT, buscar como un token de sesión (`user_email_for_session_token`), luego buscar como una clave API (`user_email_for_api_key`). El que tenga éxito primero resuelve el correo electrónico del llamador.
2. **Verificar créditos.** Antes de atender una solicitud, el backend llama a `user_has_credits(user_email)` (llamadores JWT/sesión) o `api_key_user_has_credits(api_key)` (llamadores de clave API) para confirmar que la columna `credits` del usuario en `users` es al menos 1.
3. **Deducir y registrar.** Al completarse, `deduct_credits_from_api_key_user()` decrementa el saldo y `log_api_usage()` inserta una fila en `api_usage` con el endpoint, modelo, conteos de tokens y créditos gastados — esto es lo que alimenta `GET /v1/usage` y `GET /v1/account`.
4. **Actualizar a través de Stripe.** El frontend llama a `POST /createCheckoutSession`, que accede a `CreateCheckoutSessionHandler`: resuelve al usuario, mapea el `product_hash` solicitado a un ID de precio de Stripe y crea una `stripe.checkout.Session` en modo `subscription` (opcionalmente aplicando un código de prueba gratuita de 30 días).
5. **Webhook completa el ciclo.** Stripe llama de vuelta a `POST /stripeWebhook` en `checkout.session.completed`; `StripeWebhookHandler` registra la nueva suscripción a través de `add_subscription()` y llama a `refresh_credits(user_email)` para recargar el saldo del usuario. Los eventos `customer.subscription.updated` (cancelación) y `.deleted` se manejan de manera simétrica.
6. **Gestionar la suscripción.** `POST /createPortalSession` (`CreatePortalSessionHandler`) abre una sesión del Portal de Facturación de Stripe limitada al nivel actual del usuario a través de `config_for_payment_tiers()`, por lo que las actualizaciones/bajas/cancelaciones ocurren a través de la interfaz alojada de Stripe.
7. **Claves API.** `POST /generateAPIKey` requiere al menos 1 crédito y llama a `generate_api_key()`; `GET /getAPIKeys` y `POST /deleteAPIKey` listan/revokan claves, cada una rastreada con una marca de tiempo `last_used` (`touch_api_key_last_used`).

### Medidas de protección contra abusos

`verifyAuthForNewSubscriptipns()` en `db_auth.py` limita las nuevas suscripciones por nivel por día (por ejemplo, 25/día para Premium, 5/día para Enterprise), envía una alerta interna por correo electrónico en umbrales definidos (5, 10, 50, 100, 200, 500 nuevas suscripciones/día) y bloquea a un usuario de cambiar de plan más de una vez en un mes móvil.

## Ejecútalo localmente

Desde la raíz del espacio de trabajo (`anote/panacea`):

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

Configura estos en `backend/.env` para ejercitar el flujo de facturación:

```bash
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
FRONTEND_URL=http://localhost:3000
JWT_SECRET_KEY=some-dev-secret
```

Reenvía los webhooks de Stripe a tu backend local con el Stripe CLI:

```bash
stripe listen --forward-to localhost:5000/stripeWebhook
```

### Pruébalo

```bash
# Generar una clave API (requiere un JWT/sesión autenticada, y >=1 crédito)
curl -X POST http://localhost:5000/generateAPIKey \
  -H "Authorization: Bearer <jwt_or_session_token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "mi primera clave"}'

# Verificar uso con la nueva clave API
curl http://localhost:5000/v1/usage \
  -H "Authorization: Bearer <api_key>"
```

## Notas para el recetario

Combina esto con la receta 07 (Puerta de enlace API compatible con OpenAI): las mismas claves API generadas aquí son las que autentican las llamadas a `AnoteOpenAI`. Vale la pena señalar el error tipográfico `verifyAuthForNewSubscriptipns` en el nombre de la función como una peculiaridad conocida si un lector lo busca en el código.
