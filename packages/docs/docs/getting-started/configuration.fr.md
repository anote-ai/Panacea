# Configuration

## Configuration CLI

La configuration est stockée dans `~/.anote/config.json` :

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

Gérez via :

```bash
anote config set model claude-opus-4-8
anote config get model
anote config list
```

## Variables d'environnement

Tous les paramètres peuvent être remplacés par des variables d'environnement :

| Variable | But |
|---|---|
| `ANTHROPIC_API_KEY` | Clé API Anthropic |
| `OPENAI_API_KEY` | Clé API OpenAI |
| `GEMINI_API_KEY` | Clé API Google Gemini |
| `ANOTE_MODEL` | Modèle par défaut |
| `ANOTE_SERVER_URL` | URL du backend Anote |

## Configuration Backend

Copiez `packages/backend/.env.example` dans `packages/backend/.env` et remplissez :

```bash
# Fournisseurs LLM
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...

# Base de données
DB_HOST=localhost
DB_NAME=anote
DB_USER=anote
DB_PASSWORD=anote

# Auth
JWT_SECRET_KEY=your-secret-key

# Paiements (optionnel)
STRIPE_SECRET_KEY=sk_...
```
