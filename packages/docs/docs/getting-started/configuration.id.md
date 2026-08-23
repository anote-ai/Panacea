# Konfigurasi

## Konfigurasi CLI

Konfigurasi disimpan di `~/.anote/config.json`:

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

Kelola melalui:

```bash
anote config set model claude-opus-4-8
anote config get model
anote config list
```

## Variabel Lingkungan

Semua pengaturan dapat ditimpa dengan variabel lingkungan:

| Variabel | Tujuan |
|---|---|
| `ANTHROPIC_API_KEY` | Kunci API Anthropic |
| `OPENAI_API_KEY` | Kunci API OpenAI |
| `GEMINI_API_KEY` | Kunci API Google Gemini |
| `ANOTE_MODEL` | Model default |
| `ANOTE_SERVER_URL` | URL backend Anote |

## Konfigurasi Backend

Salin `packages/backend/.env.example` ke `packages/backend/.env` dan isi:

```bash
# Penyedia LLM
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...

# Database
DB_HOST=localhost
DB_NAME=anote
DB_USER=anote
DB_PASSWORD=anote

# Auth
JWT_SECRET_KEY=your-secret-key

# Pembayaran (opsional)
STRIPE_SECRET_KEY=sk_...
```
