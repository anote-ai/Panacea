# Panacea 청구, API 키 및 크레딧 측정

이 레시피는 Panacea가 사용량을 측정하고, API 호출자를 인증하며, Stripe 구독을 사용 가능한 크레딧 잔액으로 전환하는 방법을 설명합니다.

## 배울 내용

- 요청을 인증할 수 있는 세 가지 방법: JWT, 세션 토큰 또는 장기 API 키
- 요청당 크레딧이 어떻게 확인되고 차감되는지, 사용량이 어떻게 기록되는지
- Stripe 구독 체크아웃이 새로 고쳐진 크레딧 잔액으로 흐르는 방법
- 사용자가 자신의 API 키를 생성, 나열 및 취소하는 방법
- 새로운/변경된 구독을 제한하는 남용 방지 장치

## 왜 이것이 중요한가

Panacea는 단순한 RAG 데모가 아닙니다 — 실제 구독 계층이 있는 측정된 제품입니다. 문서 업로드, 채팅 완료 또는 평가 호출마다 크레딧이 소모되며, 크레딧은 활성 Stripe 구독에 의해 보충됩니다. 이 레시피는 호출자가 자신이 누구인지 증명하는 방법, 그 신원이 어떻게 가격이 매겨지는지, 그리고 돈(Stripe를 통해)이 어떻게 사용 가능한 크레딧으로 전환되는지를 설명합니다.

## 주요 Panacea 파일

| 파일 | 중요성 |
|---|---|
| `Panacea/backend/database/db_auth.py` | `extractUserEmailFromRequest()`는 JWT → 세션 토큰 → API 키 순서로 시도합니다; `user_has_credits()`, `api_key_user_has_credits()`, `deduct_credits_from_api_key_user()`; `verifyAuthForNewSubscriptipns()`의 남용 방지 장치 |
| `Panacea/backend/database/usage.py` | `log_api_usage()`는 요청당 한 행을 `api_usage`에 기록합니다; `get_usage_summary()` / `get_usage_rows()`는 사용량 보고를 지원합니다 |
| `Panacea/backend/api_endpoints/payments/handler.py` | `CreateCheckoutSessionHandler`, `CreatePortalSessionHandler`, `StripeWebhookHandler` |
| `Panacea/backend/api_endpoints/generate_api_key/handler.py`, `get_api_keys/handler.py`, `delete_api_key/handler.py`, `refresh_credits/handler.py` | API 키를 생성, 나열, 취소합니다; 크레딧을 수동으로 새로 고칩니다 |
| `Panacea/backend/stripe_config/portal_config.py` | 계층별 Stripe 청구 포털 구성 |

## 작동 방식

1. **인증.** 모든 보호된 경로는 `extractUserEmailFromRequest(request)`를 호출하여 `Authorization: Bearer <token>` 헤더를 읽고, 순서대로 시도합니다: JWT로 디코드, 세션 토큰으로 조회(`user_email_for_session_token`), 그리고 API 키로 조회(`user_email_for_api_key`). 가장 먼저 성공하는 것이 호출자의 이메일을 해결합니다.
2. **크레딧 확인.** 요청을 제공하기 전에 백엔드는 `user_has_credits(user_email)` (JWT/세션 호출자) 또는 `api_key_user_has_credits(api_key)` (API 키 호출자)를 호출하여 사용자의 `users`의 `credits` 열이 최소 1인지 확인합니다.
3. **차감 및 기록.** 완료 시, `deduct_credits_from_api_key_user()`는 잔액을 차감하고 `log_api_usage()`는 엔드포인트, 모델, 토큰 수 및 소모된 크레딧과 함께 `api_usage`에 행을 삽입합니다 — 이는 `GET /v1/usage` 및 `GET /v1/account`를 지원합니다.
4. **Stripe를 통한 업그레이드.** 프론트엔드는 `POST /createCheckoutSession`을 호출하여 `CreateCheckoutSessionHandler`에 도달합니다: 사용자를 해결하고 요청된 `product_hash`를 Stripe 가격 ID에 매핑하며, `subscription` 모드에서 `stripe.checkout.Session`을 생성합니다(선택적으로 30일 무료 체험 코드를 적용).
5. **Webhook이 루프를 완료합니다.** Stripe는 `checkout.session.completed`에서 `POST /stripeWebhook`를 호출합니다; `StripeWebhookHandler`는 `add_subscription()`을 통해 새로운 구독을 기록하고 `refresh_credits(user_email)`를 호출하여 사용자의 잔액을 보충합니다. `customer.subscription.updated`(취소) 및 `.deleted` 이벤트는 대칭적으로 처리됩니다.
6. **구독 관리.** `POST /createPortalSession` (`CreatePortalSessionHandler`)는 사용자의 현재 계층에 맞춘 Stripe 청구 포털 세션을 엽니다(`config_for_payment_tiers()`를 통해), 따라서 업그레이드/다운그레이드/취소는 Stripe의 호스팅 UI를 통해 발생합니다.
7. **API 키.** `POST /generateAPIKey`는 최소 1 크레딧을 요구하며 `generate_api_key()`를 호출합니다; `GET /getAPIKeys` 및 `POST /deleteAPIKey`는 키를 나열/취소하며, 각 키는 `last_used` 타임스탬프(`touch_api_key_last_used`)로 추적됩니다.

### 남용 방지 장치

`db_auth.py`의 `verifyAuthForNewSubscriptipns()`는 계층당 하루에 새로운 구독 수를 제한합니다(예: 프리미엄은 25/일, 엔터프라이즈는 5/일), 정의된 임계값(5, 10, 50, 100, 200, 500 새로운 구독/일)에서 내부 경고 이메일을 발송하며, 사용자가 한 달 내에 플랜을 변경하는 것을 한 번 이상 차단합니다.

## 로컬에서 실행하기

작업 공간 루트(`anote/panacea`)에서:

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

청구 흐름을 실행하기 위해 `backend/.env`에 다음을 설정합니다:

```bash
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
FRONTEND_URL=http://localhost:3000
JWT_SECRET_KEY=some-dev-secret
```

Stripe CLI를 사용하여 Stripe 웹훅을 로컬 백엔드로 전달합니다:

```bash
stripe listen --forward-to localhost:5000/stripeWebhook
```

### 시도해보기

```bash
# API 키 생성 (인증된 JWT/세션 및 >=1 크레딧 필요)
curl -X POST http://localhost:5000/generateAPIKey \
  -H "Authorization: Bearer <jwt_or_session_token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "my first key"}'

# 새 API 키로 사용량 확인
curl http://localhost:5000/v1/usage \
  -H "Authorization: Bearer <api_key>"
```

## 요리책을 위한 노트

이 레시피는 레시피 07 (OpenAI 호환 API 게이트웨이)와 함께 사용하세요 — 여기에서 생성된 동일한 API 키가 `AnoteOpenAI` 호출을 인증하는 데 사용됩니다. 독자가 코드에서 이를 찾으려 할 경우 함수 이름의 `verifyAuthForNewSubscriptipns` 오타를 알려진 특이점으로 플래그하는 것이 좋습니다.
