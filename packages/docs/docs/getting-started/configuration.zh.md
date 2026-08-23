# 配置

## CLI 配置

配置存储在 `~/.anote/config.json` 中：

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

通过以下命令管理：

```bash
anote config set model claude-opus-4-8
anote config get model
anote config list
```

## 环境变量

所有设置可以通过环境变量覆盖：

| 变量 | 目的 |
|---|---|
| `ANTHROPIC_API_KEY` | Anthropic API 密钥 |
| `OPENAI_API_KEY` | OpenAI API 密钥 |
| `GEMINI_API_KEY` | Google Gemini API 密钥 |
| `ANOTE_MODEL` | 默认模型 |
| `ANOTE_SERVER_URL` | Anote 后端 URL |

## 后端配置

将 `packages/backend/.env.example` 复制到 `packages/backend/.env` 并填写：

```bash
# LLM 提供者
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...

# 数据库
DB_HOST=localhost
DB_NAME=anote
DB_USER=anote
DB_PASSWORD=anote

# 认证
JWT_SECRET_KEY=your-secret-key

# 支付（可选）
STRIPE_SECRET_KEY=sk_...
```
