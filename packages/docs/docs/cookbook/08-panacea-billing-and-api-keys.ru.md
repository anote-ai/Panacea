# Панасея: Выставление счетов, API-ключи и учет кредитов

Этот рецепт объясняет, как Панасея учитывает использование, аутентифицирует вызовы API и превращает подписки Stripe в доступный кредитный баланс.

## Что вы узнаете

- Три способа аутентификации запроса: JWT, токен сессии или долгоживущий API-ключ
- Как проверяются и вычитаются кредиты за каждый запрос, и как фиксируется использование
- Как процесс оформления подписки Stripe приводит к обновлению кредитного баланса
- Как пользователи генерируют, перечисляют и аннулируют свои собственные API-ключи
- Ограничения на злоупотребления, которые контролируют новые/измененные подписки

## Почему это важно

Панасея — это не просто демонстрация RAG — это продукт с учетом использования и реальными уровнями подписки. Каждая загрузка документа, завершение чата или вызов оценки стоят кредитов, а кредиты пополняются активной подпиской Stripe. Этот рецепт описывает полный цикл: как вызывающий доказывает, кто он есть, как эта идентичность оценивается и как деньги (через Stripe) превращаются обратно в используемые кредиты.

## Ключевые файлы Панасеи

| Файл | Почему это важно |
|---|---|
| `Panacea/backend/database/db_auth.py` | `extractUserEmailFromRequest()` пытается последовательно использовать JWT → токен сессии → API-ключ; `user_has_credits()`, `api_key_user_has_credits()`, `deduct_credits_from_api_key_user()`; ограничения на злоупотребления в `verifyAuthForNewSubscriptipns()` |
| `Panacea/backend/database/usage.py` | `log_api_usage()` записывает одну строку за запрос в `api_usage`; `get_usage_summary()` / `get_usage_rows()` обеспечивают отчетность по использованию |
| `Panacea/backend/api_endpoints/payments/handler.py` | `CreateCheckoutSessionHandler`, `CreatePortalSessionHandler`, `StripeWebhookHandler` |
| `Panacea/backend/api_endpoints/generate_api_key/handler.py`, `get_api_keys/handler.py`, `delete_api_key/handler.py`, `refresh_credits/handler.py` | Генерация, перечисление, аннулирование API-ключей; ручное обновление кредитов |
| `Panacea/backend/stripe_config/portal_config.py` | Конфигурация Stripe Billing Portal для каждого уровня |

## Как это работает

1. **Аутентификация.** Каждый защищенный маршрут вызывает `extractUserEmailFromRequest(request)`, который читает заголовок `Authorization: Bearer <token>` и пытается в следующем порядке: декодировать как JWT, найти как токен сессии (`user_email_for_session_token`), затем найти как API-ключ (`user_email_for_api_key`). То, что сработает первым, определяет email вызывающего.
2. **Проверка кредитов.** Перед обслуживанием запроса бэкенд вызывает `user_has_credits(user_email)` (для вызовов JWT/сессии) или `api_key_user_has_credits(api_key)` (для вызовов API-ключа), чтобы подтвердить, что колонка `credits` пользователя в `users` составляет не менее 1.
3. **Вычет и логирование.** По завершении `deduct_credits_from_api_key_user()` уменьшает баланс, а `log_api_usage()` вставляет строку в `api_usage` с конечной точкой, моделью, количеством токенов и потраченными кредитами — это то, что обеспечивает работу `GET /v1/usage` и `GET /v1/account`.
4. **Обновление через Stripe.** Фронтенд вызывает `POST /createCheckoutSession`, который попадает в `CreateCheckoutSessionHandler`: он определяет пользователя, сопоставляет запрашиваемый `product_hash` с ID цены Stripe и создает `stripe.checkout.Session` в режиме подписки (опционально применяя код на 30-дневный бесплатный пробный период).
5. **Webhook завершает цикл.** Stripe вызывает `POST /stripeWebhook` на `checkout.session.completed`; `StripeWebhookHandler` фиксирует новую подписку через `add_subscription()` и вызывает `refresh_credits(user_email)`, чтобы пополнить баланс пользователя. События `customer.subscription.updated` (отмена) и `.deleted` обрабатываются симметрично.
6. **Управление подпиской.** `POST /createPortalSession` (`CreatePortalSessionHandler`) открывает сессию Stripe Billing Portal, ограниченную текущим уровнем пользователя через `config_for_payment_tiers()`, так что обновления/понижения/отмены происходят через хостируемый интерфейс Stripe.
7. **API-ключи.** `POST /generateAPIKey` требует как минимум 1 кредит и вызывает `generate_api_key()`; `GET /getAPIKeys` и `POST /deleteAPIKey` перечисляют/аннулируют ключи, каждый из которых отслеживается с помощью временной метки `last_used` (`touch_api_key_last_used`).

### Ограничения на злоупотребления

`verifyAuthForNewSubscriptipns()` в `db_auth.py` ограничивает новые подписки по уровню в день (например, 25/день для Premium, 5/день для Enterprise), отправляет внутреннее уведомление по электронной почте при достижении определенных порогов (5, 10, 50, 100, 200, 500 новых подписок/день) и блокирует пользователя от изменения планов более одного раза в течение текущего месяца.

## Запустите это локально

Из корня рабочего пространства (`anote/panacea`):

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

Установите эти параметры в `backend/.env`, чтобы протестировать процесс выставления счетов:

```bash
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
FRONTEND_URL=http://localhost:3000
JWT_SECRET_KEY=some-dev-secret
```

Перенаправьте вебхуки Stripe на ваш локальный бэкенд с помощью Stripe CLI:

```bash
stripe listen --forward-to localhost:5000/stripeWebhook
```

### Попробуйте это

```bash
# Сгенерировать API-ключ (требуется аутентифицированный JWT/сессия и >=1 кредит)
curl -X POST http://localhost:5000/generateAPIKey \
  -H "Authorization: Bearer <jwt_or_session_token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "my first key"}'

# Проверить использование с новым API-ключом
curl http://localhost:5000/v1/usage \
  -H "Authorization: Bearer <api_key>"
```

## Заметки для кулинарной книги

Сочетайте это с рецептом 07 (Совместимый с OpenAI API Gateway) — те же API-ключи, сгенерированные здесь, аутентифицируют вызовы `AnoteOpenAI`. Стоит отметить опечатку в имени функции `verifyAuthForNewSubscriptipns` как известную особенность, если читатель будет искать ее в коде.
