# Konfiguration

## CLI-Konfiguration

Die Konfiguration wird in `~/.anote/config.json` gespeichert:

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

Verwalten über:

```bash
anote config set model claude-opus-4-8
anote config get model
anote config list
```

## Umgebungsvariablen

Alle Einstellungen können mit Umgebungsvariablen überschrieben werden:

| Variable | Zweck |
|---|---|
| `ANTHROPIC_API_KEY` | Anthropic API-Schlüssel |
| `OPENAI_API_KEY` | OpenAI API-Schlüssel |
| `GEMINI_API_KEY` | Google Gemini API-Schlüssel |
| `ANOTE_MODEL` | Standardmodell |
| `ANOTE_SERVER_URL` | Anote Backend-URL |

## Backend-Konfiguration

Kopiere `packages/backend/.env.example` nach `packages/backend/.env` und fülle es aus:

```bash
# LLM-Anbieter
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...

# Datenbank
DB_HOST=localhost
DB_NAME=anote
DB_USER=anote
DB_PASSWORD=anote

# Auth
JWT_SECRET_KEY=your-secret-key

# Zahlungen (optional)
STRIPE_SECRET_KEY=sk_...
```
