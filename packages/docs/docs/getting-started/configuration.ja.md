# 設定

## CLI 設定

設定は `~/.anote/config.json` に保存されます:

```json
{
  "model": "claude-sonnet-4-6",
  "provider": "anthropic",
  "apiKey": "sk-ant-...",
  "serverUrl": "http://localhost:5000",
  "maxTurns": 30,
  "permissionMode": "default"
}
```

次のコマンドで管理します:

```bash
anote config set model claude-opus-4-8
anote config get model
anote config list
```

## 環境変数

すべての設定は環境変数で上書きできます:

| 変数 | 目的 |
|---|---|
| `ANTHROPIC_API_KEY` | Anthropic API キー |
| `OPENAI_API_KEY` | OpenAI API キー |
| `GEMINI_API_KEY` | Google Gemini API キー |
| `ANOTE_MODEL` | デフォルトモデル |
| `ANOTE_SERVER_URL` | Anote バックエンド URL |

## バックエンド設定

`packages/backend/.env.example` を `packages/backend/.env` にコピーし、以下を記入します:

```bash
# LLM プロバイダー
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...

# データベース
DB_HOST=localhost
DB_NAME=anote
DB_USER=anote
DB_PASSWORD=anote

# 認証
JWT_SECRET_KEY=your-secret-key

# 支払い (オプション)
STRIPE_SECRET_KEY=sk_...
```
