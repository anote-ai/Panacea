# バックエンド API 概要

Anote バックエンドは、すべてのクライアントインターフェースにサービスを提供する統一された Flask API です。

基本 URL: `http://localhost:5000` (ローカル) またはデプロイされたバックエンドの URL。

## 認証

すべての保護されたエンドポイントは JWT トークンを必要とします：

```
Authorization: Bearer <token>
```

トークンは `POST /auth/login` または `POST /auth/register` を通じて取得します。

## 主要エンドポイント

### エージェントチャット (ストリーミング)

```
POST /api/chat/stream          # SSE ストリーミングチャット
POST /api/chat                 # 非ストリーミングチャット
GET  /api/chat/sessions        # セッションのリスト
POST /api/chat/sessions        # セッションの作成
```

### ドキュメント

```
POST /api/documents/upload     # ドキュメントのアップロード
GET  /api/documents            # ドキュメントのリスト
GET  /api/documents/{id}       # ドキュメントの取得
DELETE /api/documents/{id}     # ドキュメントの削除
POST /api/documents/{id}/ask   # ドキュメントに関する Q&A
```

### セマンティック検索

```
GET  /api/search?q=...&cwd=... # インデックスされたコードベースの検索
```

### 認証

```
POST /auth/register            # 登録
POST /auth/login               # ログイン
POST /auth/refresh             # JWT のリフレッシュ
GET  /auth/google              # Google OAuth
```

### ユーザー & 請求

```
GET  /api/user/profile         # ユーザーの取得
POST /api/payments/checkout    # Stripe チェックアウト
POST /api/payments/portal      # カスタマーポータル
POST /api/payments/webhook     # Stripe ウェブフック
```
