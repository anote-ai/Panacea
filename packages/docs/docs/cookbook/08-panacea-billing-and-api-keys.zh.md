# Panacea 计费、API 密钥与信用计量

本食谱解释了 Panacea 如何计量使用情况、验证 API 调用者，并将 Stripe 订阅转换为可支配的信用余额。

## 您将学到的内容

- 请求可以通过三种方式进行身份验证：JWT、会话令牌或长期 API 密钥
- 如何检查和扣除每个请求的信用，以及如何记录使用情况
- Stripe 订阅结账如何流转到更新的信用余额
- 用户如何生成、列出和撤销自己的 API 密钥
- 防止滥用的保护措施，限制新的/更改的订阅

## 这很重要的原因

Panacea 不仅仅是一个 RAG 演示 — 它是一个具有真实订阅层级的计量产品。每次文档上传、聊天完成或评估调用都会消耗信用，而信用通过有效的 Stripe 订阅进行补充。本食谱详细介绍了整个循环：调用者如何证明他们的身份，这种身份的定价方式，以及资金（通过 Stripe）如何转化为可用的信用。

## 关键的 Panacea 文件

| 文件 | 重要性 |
|---|---|
| `Panacea/backend/database/db_auth.py` | `extractUserEmailFromRequest()` 按顺序尝试 JWT → 会话令牌 → API 密钥；`user_has_credits()`、`api_key_user_has_credits()`、`deduct_credits_from_api_key_user()`；在 `verifyAuthForNewSubscriptipns()` 中的滥用保护措施 |
| `Panacea/backend/database/usage.py` | `log_api_usage()` 每个请求写入一行到 `api_usage`；`get_usage_summary()` / `get_usage_rows()` 提供使用情况报告 |
| `Panacea/backend/api_endpoints/payments/handler.py` | `CreateCheckoutSessionHandler`、`CreatePortalSessionHandler`、`StripeWebhookHandler` |
| `Panacea/backend/api_endpoints/generate_api_key/handler.py`、`get_api_keys/handler.py`、`delete_api_key/handler.py`、`refresh_credits/handler.py` | 生成、列出、撤销 API 密钥；手动刷新信用 |
| `Panacea/backend/stripe_config/portal_config.py` | 每个层级的 Stripe 计费门户配置 |

## 工作原理

1. **身份验证。** 每个受保护的路由调用 `extractUserEmailFromRequest(request)`，该函数读取 `Authorization: Bearer <token>` 头并按顺序尝试：解码为 JWT、查找为会话令牌（`user_email_for_session_token`），然后查找为 API 密钥（`user_email_for_api_key`）。第一个成功的将解析调用者的电子邮件。
2. **检查信用。** 在处理请求之前，后端调用 `user_has_credits(user_email)`（JWT/会话调用者）或 `api_key_user_has_credits(api_key)`（API 密钥调用者）以确认用户的 `users` 表中的 `credits` 列至少为 1。
3. **扣除和记录。** 完成后，`deduct_credits_from_api_key_user()` 减少余额，`log_api_usage()` 向 `api_usage` 插入一行，包含端点、模型、令牌计数和消耗的信用 — 这为 `GET /v1/usage` 和 `GET /v1/account` 提供支持。
4. **通过 Stripe 升级。** 前端调用 `POST /createCheckoutSession`，该请求触发 `CreateCheckoutSessionHandler`：它解析用户，将请求的 `product_hash` 映射到 Stripe 价格 ID，并在 `subscription` 模式下创建 `stripe.checkout.Session`（可选择应用 30 天的免费试用代码）。
5. **Webhook 完成循环。** Stripe 在 `checkout.session.completed` 上回调 `POST /stripeWebhook`；`StripeWebhookHandler` 通过 `add_subscription()` 记录新的订阅，并调用 `refresh_credits(user_email)` 来补充用户的余额。`customer.subscription.updated`（取消）和 `.deleted` 事件对称处理。
6. **管理订阅。** `POST /createPortalSession`（`CreatePortalSessionHandler`）打开一个针对用户当前层级的 Stripe 计费门户会话，通过 `config_for_payment_tiers()`，因此升级/降级/取消通过 Stripe 的托管 UI 进行。
7. **API 密钥。** `POST /generateAPIKey` 需要至少 1 个信用并调用 `generate_api_key()`；`GET /getAPIKeys` 和 `POST /deleteAPIKey` 列出/撤销密钥，每个密钥都有一个 `last_used` 时间戳（`touch_api_key_last_used`）。

### 滥用保护措施

`verifyAuthForNewSubscriptipns()` 在 `db_auth.py` 中限制每个层级每天的新订阅数量（例如，Premium 每天 25 个，Enterprise 每天 5 个），在定义的阈值（5、10、50、100、200、500 个新订阅/天）时发送内部警报，并阻止用户在滚动的一个月内更改计划超过一次。

## 本地运行

从工作区根目录（`anote/panacea`）：

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

在 `backend/.env` 中设置这些以执行计费流程：

```bash
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
FRONTEND_URL=http://localhost:3000
JWT_SECRET_KEY=some-dev-secret
```

使用 Stripe CLI 将 Stripe Webhook 转发到您的本地后端：

```bash
stripe listen --forward-to localhost:5000/stripeWebhook
```

### 尝试一下

```bash
# 生成一个 API 密钥（需要经过身份验证的 JWT/会话，并且 >=1 个信用）
curl -X POST http://localhost:5000/generateAPIKey \
  -H "Authorization: Bearer <jwt_or_session_token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "my first key"}'

# 使用新的 API 密钥检查使用情况
curl http://localhost:5000/v1/usage \
  -H "Authorization: Bearer <api_key>"
```

## 食谱说明

将此与食谱 07（OpenAI 兼容的 API 网关）配对 — 在这里生成的相同 API 密钥用于验证 `AnoteOpenAI` 调用。如果读者在代码中寻找，值得指出函数名中的 `verifyAuthForNewSubscriptipns` 拼写错误作为已知的特性。
