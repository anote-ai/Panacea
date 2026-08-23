# Configurazione

## Configurazione CLI

La configurazione è memorizzata in `~/.anote/config.json`:

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

Gestisci tramite:

```bash
anote config set model claude-opus-4-8
anote config get model
anote config list
```

## Variabili d'Ambiente

Tutte le impostazioni possono essere sovrascritte con variabili d'ambiente:

| Variabile | Scopo |
|---|---|
| `ANTHROPIC_API_KEY` | Chiave API di Anthropic |
| `OPENAI_API_KEY` | Chiave API di OpenAI |
| `GEMINI_API_KEY` | Chiave API di Google Gemini |
| `ANOTE_MODEL` | Modello predefinito |
| `ANOTE_SERVER_URL` | URL del backend di Anote |

## Configurazione del Backend

Copia `packages/backend/.env.example` in `packages/backend/.env` e compila:

```bash
# Fornitori LLM
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...

# Database
DB_HOST=localhost
DB_NAME=anote
DB_USER=anote
DB_PASSWORD=anote

# Autenticazione
JWT_SECRET_KEY=your-secret-key

# Pagamenti (opzionale)
STRIPE_SECRET_KEY=sk_...
```
