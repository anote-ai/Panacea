# アーキテクチャ

## モノレポ構造

```
Panacea/
├── packages/
│   ├── backend/    # Python Flask — 統一API + エージェントストリーミング + RAG
│   ├── cli/        # TypeScript — anoteターミナルCLI
│   ├── vscode/     # TypeScript — VS Code拡張
│   ├── web/        # TypeScript/React — ブラウザチャットボットアプリ
│   ├── mobile/     # TypeScript/React Native (Expo) — iOS + Android
│   ├── desktop/    # TypeScript/Electron — プライベートデスクトップアプリ
│   ├── sdk/        # TypeScript — JS/TSクライアントSDK
│   └── docs/       # MkDocs Material — ドキュメントサイト
├── docker-compose.yml
├── package.json    # npmワークスペース
└── Makefile
```

## バックエンドアーキテクチャ

Python Flaskバックエンドはすべてのサーバーサイドロジックを処理します：

```
packages/backend/
├── app.py                    # Flaskエントリーポイント、ルート登録
├── api_endpoints/
│   ├── chat/                 # エージェントストリーミング (SSE)、セッション管理
│   ├── documents/            # アップロード、RAGパイプライン、Q&A
│   ├── search/               # セマンティック検索インデックスクエリ
│   ├── auth/                 # JWT、Google OAuth
│   ├── user/                 # プロフィール、設定
│   └── payments/             # Stripeウェブフック + チェックアウト
├── agents/                   # LangChain/LangGraphエージェント定義
├── services/
│   ├── rag.py                # ドキュメントチャンク + Chroma埋め込み
│   ├── streaming.py          # Claude/OpenAI/GeminiへのSSEストリーミング
│   └── search.py             # TF-IDFセマンティック検索
├── database/
│   ├── db.py                 # MySQL接続 + クエリ
│   └── schema.sql            # データベーススキーマ
└── models/                   # LLMプロバイダーラッパー
```

## データフロー: エージェントチャット

```
クライアント (CLI / VS Code / Web / Mobile)
    │  POST /api/chat/stream {message, cwd, model}
    ▼
Flaskバックエンド (app.py → chat/handler.py)
    │  SSEストリーム
    ▼
LLMプロバイダー (Anthropic / OpenAI / Gemini / Ollama)
    │  ツール呼び出し ↔ 実行 (読み取り/書き込み/編集/Bash/Glob/Grep)
    ▼
ファイルシステム (cwd) + Chroma (RAGコンテキスト)
```

## 技術選択

| レイヤー | 技術 | 理由 |
|---|---|---|
| バックエンド | Python Flask | 豊富なML/AIエコシステム、既存のエージェント |
| エージェントストリーミング | Anthropic Python SDK | ネイティブSSE、ツール使用 |
| ベクターデータベース | ChromaDB | ローカルファースト、インフラ不要 |
| データベース | MySQL | ACID、既存のスキーマ |
| キャッシュ | Redis | セッション + レート制限 |
| フロントエンド | React 18 + TypeScript | 型安全、エコシステム |
| デスクトップ | Electron | クロスプラットフォーム、Pythonをバンドル |
| モバイル | Expo (React Native) | ウェブとのコード共有 |
| CLI | Commander.js | 成熟、TypeScriptフレンドリー |
| ドキュメント | MkDocs Material | 美しい、高速、マークダウン |
