# Panacea Faturamento, Chaves de API e Medição de Crédito

Esta receita explica como a Panacea mede o uso, autentica os chamadores da API e transforma assinaturas do Stripe em um saldo de crédito utilizável.

## O que você aprenderá

- As três maneiras de uma solicitação se autenticar: JWT, token de sessão ou chave de API de longa duração
- Como os créditos são verificados e deduzidos por solicitação, e como o uso é registrado
- Como um fluxo de checkout de assinatura do Stripe se transforma em um saldo de crédito atualizado
- Como os usuários geram, listam e revogam suas próprias chaves de API
- As barreiras de abuso que controlam novas/alteradas assinaturas

## Por que isso é importante

A Panacea não é apenas uma demonstração RAG — é um produto medido com níveis de assinatura reais. Cada upload de documento, conclusão de chat ou chamada de avaliação custa créditos, e os créditos são reabastecidos por uma assinatura ativa do Stripe. Esta receita percorre todo o ciclo: como um chamador prova quem é, como essa identidade é precificada e como o dinheiro (via Stripe) se transforma novamente em créditos utilizáveis.

## Principais arquivos do Panacea

| Arquivo | Por que é importante |
|---|---|
| `Panacea/backend/database/db_auth.py` | `extractUserEmailFromRequest()` tenta JWT → token de sessão → chave de API em sequência; `user_has_credits()`, `api_key_user_has_credits()`, `deduct_credits_from_api_key_user()`; barreiras de abuso em `verifyAuthForNewSubscriptipns()` |
| `Panacea/backend/database/usage.py` | `log_api_usage()` escreve uma linha por solicitação em `api_usage`; `get_usage_summary()` / `get_usage_rows()` alimentam relatórios de uso |
| `Panacea/backend/api_endpoints/payments/handler.py` | `CreateCheckoutSessionHandler`, `CreatePortalSessionHandler`, `StripeWebhookHandler` |
| `Panacea/backend/api_endpoints/generate_api_key/handler.py`, `get_api_keys/handler.py`, `delete_api_key/handler.py`, `refresh_credits/handler.py` | Criar, listar, revogar chaves de API; atualizar créditos manualmente |
| `Panacea/backend/stripe_config/portal_config.py` | Configuração do Portal de Faturamento do Stripe por nível |

## Como funciona

1. **Autenticar.** Cada rota protegida chama `extractUserEmailFromRequest(request)`, que lê o cabeçalho `Authorization: Bearer <token>` e tenta, na ordem: decodificar como um JWT, procurar como um token de sessão (`user_email_for_session_token`), e então procurar como uma chave de API (`user_email_for_api_key`). O que tiver sucesso primeiro resolve o e-mail do chamador.
2. **Verificar créditos.** Antes de atender a uma solicitação, o backend chama `user_has_credits(user_email)` (chamadores JWT/sessão) ou `api_key_user_has_credits(api_key)` (chamadores de chave de API) para confirmar que a coluna `credits` do usuário em `users` é pelo menos 1.
3. **Deduzir e registrar.** Ao completar, `deduct_credits_from_api_key_user()` decrementa o saldo e `log_api_usage()` insere uma linha em `api_usage` com o endpoint, modelo, contagens de token e créditos gastos — isso é o que alimenta `GET /v1/usage` e `GET /v1/account`.
4. **Atualizar via Stripe.** O frontend chama `POST /createCheckoutSession`, que aciona `CreateCheckoutSessionHandler`: ele resolve o usuário, mapeia o `product_hash` solicitado para um ID de preço do Stripe e cria uma `stripe.checkout.Session` em modo de `subscription` (aplicando opcionalmente um código de teste gratuito de 30 dias).
5. **Webhook completa o ciclo.** O Stripe chama de volta `POST /stripeWebhook` em `checkout.session.completed`; `StripeWebhookHandler` registra a nova assinatura via `add_subscription()` e chama `refresh_credits(user_email)` para reabastecer o saldo do usuário. Eventos `customer.subscription.updated` (cancelamento) e `.deleted` são tratados simetricamente.
6. **Gerenciar a assinatura.** `POST /createPortalSession` (`CreatePortalSessionHandler`) abre uma sessão do Portal de Faturamento do Stripe com escopo para o nível atual do usuário via `config_for_payment_tiers()`, de modo que atualizações/diminuições/cancelamentos ocorram através da interface hospedada do Stripe.
7. **Chaves de API.** `POST /generateAPIKey` requer pelo menos 1 crédito e chama `generate_api_key()`; `GET /getAPIKeys` e `POST /deleteAPIKey` listam/revogam chaves, cada uma rastreada com um timestamp `last_used` (`touch_api_key_last_used`).

### Barreiras de abuso

`verifyAuthForNewSubscriptipns()` em `db_auth.py` limita novas assinaturas por nível por dia (por exemplo, 25/dia para Premium, 5/dia para Enterprise), envia um alerta interno por e-mail em limites definidos (5, 10, 50, 100, 200, 500 novas assinaturas/dia) e bloqueia um usuário de mudar de plano mais de uma vez em um mês contínuo.

## Execute localmente

A partir da raiz do workspace (`anote/panacea`):

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

Defina estes em `backend/.env` para exercitar o fluxo de faturamento:

```bash
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
FRONTEND_URL=http://localhost:3000
JWT_SECRET_KEY=some-dev-secret
```

Encaminhe webhooks do Stripe para seu backend local com o Stripe CLI:

```bash
stripe listen --forward-to localhost:5000/stripeWebhook
```

### Experimente

```bash
# Gere uma chave de API (requer um JWT/sessão autenticada e >=1 crédito)
curl -X POST http://localhost:5000/generateAPIKey \
  -H "Authorization: Bearer <jwt_or_session_token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "minha primeira chave"}'

# Verifique o uso com a nova chave de API
curl http://localhost:5000/v1/usage \
  -H "Authorization: Bearer <api_key>"
```

## Notas para o livro de receitas

Combine isso com a receita 07 (Gateway de API Compatível com OpenAI) — as mesmas chaves de API geradas aqui são o que autentica chamadas do `AnoteOpenAI`. Vale a pena destacar o erro de digitação `verifyAuthForNewSubscriptipns` no nome da função como uma peculiaridade conhecida se um leitor for procurá-lo no código.
