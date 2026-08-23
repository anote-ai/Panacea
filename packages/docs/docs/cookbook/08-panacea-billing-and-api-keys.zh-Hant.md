# Panacea 計費、API 金鑰與信用計量

本食譜解釋了 Panacea 如何計量使用量、驗證 API 呼叫者，並將 Stripe 訂閱轉換為可支出信用餘額。

## 您將學到什麼

- 請求可以驗證的三種方式：JWT、會話權杖或長期有效的 API 金鑰
- 如何檢查和扣除每個請求的信用，以及如何記錄使用情況
- Stripe 訂閱結帳如何流向更新的信用餘額
- 使用者如何生成、列出和撤銷自己的 API 金鑰
- 防止濫用的護欄，限制新的/變更的訂閱

## 為什麼這很重要

Panacea 不僅僅是一個 RAG 演示 — 它是一個具有實際訂閱層級的計量產品。每次文件上傳、聊天完成或評估呼叫都需要消耗信用，而信用則由有效的 Stripe 訂閱補充。本食譜將完整介紹：呼叫者如何證明自己的身份、該身份的定價方式，以及金錢（通過 Stripe）如何轉換回可用的信用。

## 主要的 Panacea 檔案

| 檔案 | 為什麼重要 |
|---|---|
| `Panacea/backend/database/db_auth.py` | `extractUserEmailFromRequest()` 依序嘗試 JWT → 會話權杖 → API 金鑰；`user_has_credits()`、`api_key_user_has_credits()`、`deduct_credits_from_api_key_user()`；`verifyAuthForNewSubscriptipns()` 中的防止濫用護欄 |
| `Panacea/backend/database/usage.py` | `log_api_usage()` 每個請求寫入一行到 `api_usage`；`get_usage_summary()` / `get_usage_rows()` 提供使用情況報告 |
| `Panacea/backend/api_endpoints/payments/handler.py` | `CreateCheckoutSessionHandler`、`CreatePortalSessionHandler`、`StripeWebhookHandler` |
| `Panacea/backend/api_endpoints/generate_api_key/handler.py`、`get_api_keys/handler.py`、`delete_api_key/handler.py`、`refresh_credits/handler.py` | 鑄造、列出、撤銷 API 金鑰；手動刷新信用 |
| `Panacea/backend/stripe_config/portal_config.py` | 每個層級的 Stripe 計費入口配置 |

## 它是如何運作的

1. **驗證。** 每個受保護的路由都會調用 `extractUserEmailFromRequest(request)`，該函數讀取 `Authorization: Bearer <token>` 標頭，並依序嘗試：解碼為 JWT、查找為會話權杖（`user_email_for_session_token`），然後查找為 API 金鑰（`user_email_for_api_key`）。第一個成功的將解析呼叫者的電子郵件。
2. **檢查信用。** 在服務請求之前，後端調用 `user_has_credits(user_email)`（JWT/會話呼叫者）或 `api_key_user_has_credits(api_key)`（API 金鑰呼叫者）以確認使用者的 `users` 表中的 `credits` 列至少為 1。
3. **扣除並記錄。** 完成後，`deduct_credits_from_api_key_user()` 會減少餘額，並且 `log_api_usage()` 會將一行插入到 `api_usage` 中，包含端點、模型、令牌計數和消耗的信用 — 這是驅動 `GET /v1/usage` 和 `GET /v1/account` 的內容。
4. **通過 Stripe 升級。** 前端調用 `POST /createCheckoutSession`，這會觸發 `CreateCheckoutSessionHandler`：它解析使用者，將請求的 `product_hash` 映射到 Stripe 價格 ID，並在 `訂閱` 模式下創建 `stripe.checkout.Session`（可選地應用 30 天免費試用代碼）。
5. **Webhook 完成循環。** Stripe 會回調 `POST /stripeWebhook` 在 `checkout.session.completed`；`StripeWebhookHandler` 通過 `add_subscription()` 記錄新的訂閱，並調用 `refresh_credits(user_email)` 以補充使用者的餘額。`customer.subscription.updated`（取消）和 `.deleted` 事件對稱處理。
6. **管理訂閱。** `POST /createPortalSession`（`CreatePortalSessionHandler`）打開一個針對使用者當前層級的 Stripe 計費入口會話，通過 `config_for_payment_tiers()`，因此升級/降級/取消都通過 Stripe 的託管 UI 進行。
7. **API 金鑰。** `POST /generateAPIKey` 需要至少 1 個信用並調用 `generate_api_key()`；`GET /getAPIKeys` 和 `POST /deleteAPIKey` 列出/撤銷金鑰，每個金鑰都有 `last_used` 時間戳（`touch_api_key_last_used`）進行追蹤。

### 防止濫用的護欄

`verifyAuthForNewSubscriptipns()` 在 `db_auth.py` 中限制每個層級每天的新訂閱數量（例如，Premium 每天 25 個，Enterprise 每天 5 個），在定義的閾值（5、10、50、100、200、500 新訂閱/天）時發送內部警報，並阻止使用者在滾動月份內更改計劃超過一次。

## 本地運行

從工作區根目錄（`anote/panacea`）：

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

在 `backend/.env` 中設置這些以執行計費流程：

```bash
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
FRONTEND_URL=http://localhost:3000
JWT_SECRET_KEY=some-dev-secret
```

使用 Stripe CLI 將 Stripe webhook 轉發到您的本地後端：

```bash
stripe listen --forward-to localhost:5000/stripeWebhook
```

### 嘗試一下

```bash
# 生成一個 API 金鑰（需要經過身份驗證的 JWT/會話，並且 >=1 個信用）
curl -X POST http://localhost:5000/generateAPIKey \
  -H "Authorization: Bearer <jwt_or_session_token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "my first key"}'

# 使用新的 API 金鑰檢查使用情況
curl http://localhost:5000/v1/usage \
  -H "Authorization: Bearer <api_key>"
```

## 食譜的注意事項

將此與食譜 07（OpenAI 兼容的 API 閘道）配對 — 此處生成的相同 API 金鑰用於驗證 `AnoteOpenAI` 呼叫。如果讀者在代碼中尋找，值得標記 `verifyAuthForNewSubscriptipns` 函數名稱中的拼寫錯誤作為已知的特點。
