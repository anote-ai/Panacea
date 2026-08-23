# 配置

## CLI 配置

配置儲存在 `~/.anote/config.json`：

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

透過以下命令管理：

```bash
anote config set model claude-opus-4-8
anote config get model
anote config list
```

## 環境變數

所有設置可以透過環境變數覆蓋：

| 變數 | 目的 |
|---|---|
| `ANTHROPIC_API_KEY` | Anthropic API 權杖 |
| `OPENAI_API_KEY` | OpenAI API 權杖 |
| `GEMINI_API_KEY` | Google Gemini API 權杖 |
| `ANOTE_MODEL` | 預設模型 |
| `ANOTE_SERVER_URL` | Anote 後端 URL |

## 後端配置

將 `packages/backend/.env.example` 複製到 `packages/backend/.env` 並填寫：

```bash
# LLM 提供者
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...

# 資料庫
DB_HOST=localhost
DB_NAME=anote
DB_USER=anote
DB_PASSWORD=anote

# 認證
JWT_SECRET_KEY=your-secret-key

# 付款（可選）
STRIPE_SECRET_KEY=sk_...
```
