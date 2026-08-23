# Panacea 請求書、API キー & クレジットメーター

このレシピでは、Panacea が使用量を測定し、API 呼び出しを認証し、Stripe サブスクリプションを使えるクレジット残高に変換する方法を説明します。

## 学べること

- リクエストが認証される 3 つの方法: JWT、セッショントークン、または長期 API キー
- クレジットがリクエストごとにどのように確認され、差し引かれるか、そして使用量がどのように記録されるか
- Stripe サブスクリプションのチェックアウトがどのようにリフレッシュされたクレジット残高に流れるか
- ユーザーが自分の API キーを生成、リスト、取り消す方法
- 新しい/変更されたサブスクリプションを制御するための不正使用防止策

## なぜこれが重要か

Panacea は単なる RAG デモではなく、実際のサブスクリプション層を持つメーター製品です。すべてのドキュメントアップロード、チャット完了、または評価呼び出しにはクレジットが必要で、クレジットはアクティブな Stripe サブスクリプションによって補充されます。このレシピでは、呼び出し元が自分が誰であるかを証明する方法、そのアイデンティティがどのように価格設定されるか、そしてお金（Stripe 経由）がどのように使えるクレジットに戻るかの全体の流れを説明します。

## 主要な Panacea ファイル

| ファイル | 重要な理由 |
|---|---|
| `Panacea/backend/database/db_auth.py` | `extractUserEmailFromRequest()` は JWT → セッショントークン → API キーを順に試行します; `user_has_credits()`, `api_key_user_has_credits()`, `deduct_credits_from_api_key_user()`; `verifyAuthForNewSubscriptipns()` における不正使用防止策 |
| `Panacea/backend/database/usage.py` | `log_api_usage()` はリクエストごとに `api_usage` に 1 行を書き込みます; `get_usage_summary()` / `get_usage_rows()` が使用量レポートを提供します |
| `Panacea/backend/api_endpoints/payments/handler.py` | `CreateCheckoutSessionHandler`, `CreatePortalSessionHandler`, `StripeWebhookHandler` |
| `Panacea/backend/api_endpoints/generate_api_key/handler.py`, `get_api_keys/handler.py`, `delete_api_key/handler.py`, `refresh_credits/handler.py` | API キーを生成、リスト、取り消します; クレジットを手動でリフレッシュします |
| `Panacea/backend/stripe_config/portal_config.py` | 各層の Stripe 請求ポータル設定 |

## 仕組み

1. **認証。** すべての保護されたルートは `extractUserEmailFromRequest(request)` を呼び出し、`Authorization: Bearer <token>` ヘッダーを読み取り、順に試行します: JWT としてデコード、セッショントークンとして検索 (`user_email_for_session_token`)、次に API キーとして検索 (`user_email_for_api_key`)。最初に成功したものが呼び出し元のメールを解決します。
2. **クレジットを確認。** リクエストを処理する前に、バックエンドは `user_has_credits(user_email)` (JWT/セッション呼び出し元) または `api_key_user_has_credits(api_key)` (API キー呼び出し元) を呼び出して、`users` の `credits` 列が少なくとも 1 であることを確認します。
3. **差し引いて記録。** 完了時に、`deduct_credits_from_api_key_user()` は残高を減少させ、`log_api_usage()` はエンドポイント、モデル、トークン数、消費されたクレジットを含む行を `api_usage` に挿入します — これが `GET /v1/usage` と `GET /v1/account` を動かします。
4. **Stripe 経由でアップグレード。** フロントエンドは `POST /createCheckoutSession` を呼び出し、`CreateCheckoutSessionHandler` にヒットします: ユーザーを解決し、要求された `product_hash` を Stripe 価格 ID にマッピングし、`subscription` モードで `stripe.checkout.Session` を作成します（オプションで 30 日間の無料トライアルコードを適用します）。
5. **Webhook がループを完了。** Stripe は `checkout.session.completed` で `POST /stripeWebhook` を呼び出し、`StripeWebhookHandler` は `add_subscription()` を介して新しいサブスクリプションを記録し、`refresh_credits(user_email)` を呼び出してユーザーの残高を補充します。`customer.subscription.updated`（キャンセル）および `.deleted` イベントは対称的に処理されます。
6. **サブスクリプションを管理。** `POST /createPortalSession` (`CreatePortalSessionHandler`) は、`config_for_payment_tiers()` を介してユーザーの現在の層にスコープされた Stripe 請求ポータルセッションを開くため、アップグレード/ダウングレード/キャンセルは Stripe のホスティング UI を通じて行われます。
7. **API キー。** `POST /generateAPIKey` は少なくとも 1 つのクレジットを必要とし、`generate_api_key()` を呼び出します; `GET /getAPIKeys` および `POST /deleteAPIKey` はキーをリスト/取り消しし、それぞれ `last_used` タイムスタンプ（`touch_api_key_last_used`）で追跡されます。

### 不正使用防止策

`db_auth.py` の `verifyAuthForNewSubscriptipns()` は、層ごとに新しいサブスクリプションを 1 日あたり制限します（例: プレミアムは 25 件/日、エンタープライズは 5 件/日）、定義された閾値（5、10、50、100、200、500 新しいサブスクリプション/日）で内部アラートをメールし、ユーザーがローリング月間でプランを変更する回数を 1 回以上に制限します。

## ローカルで実行

ワークスペースのルートから (`anote/panacea`):

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

請求フローを実行するために `backend/.env` にこれらを設定します:

```bash
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
FRONTEND_URL=http://localhost:3000
JWT_SECRET_KEY=some-dev-secret
```

Stripe CLI を使用して、Stripe Webhook をローカルバックエンドに転送します:

```bash
stripe listen --forward-to localhost:5000/stripeWebhook
```

### 試してみる

```bash
# API キーを生成します（認証された JWT/セッションと >=1 クレジットが必要）
curl -X POST http://localhost:5000/generateAPIKey \
  -H "Authorization: Bearer <jwt_or_session_token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "my first key"}'

# 新しい API キーで使用量を確認します
curl http://localhost:5000/v1/usage \
  -H "Authorization: Bearer <api_key>"
```

## クックブックのノート

これをレシピ 07 (OpenAI 対応 API ゲートウェイ) と組み合わせてください — ここで生成された同じ API キーが `AnoteOpenAI` 呼び出しを認証します。読者がコード内で探す場合に備えて、関数名の `verifyAuthForNewSubscriptipns` の誤字を既知の特異点として指摘する価値があります。
