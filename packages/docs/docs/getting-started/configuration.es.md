# Configuración

## Configuración de CLI

La configuración se almacena en `~/.anote/config.json`:

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

Gestionar a través de:

```bash
anote config set model claude-opus-4-8
anote config get model
anote config list
```

## Variables de Entorno

Todas las configuraciones se pueden sobrescribir con variables de entorno:

| Variable | Propósito |
|---|---|
| `ANTHROPIC_API_KEY` | Clave API de Anthropic |
| `OPENAI_API_KEY` | Clave API de OpenAI |
| `GEMINI_API_KEY` | Clave API de Google Gemini |
| `ANOTE_MODEL` | Modelo por defecto |
| `ANOTE_SERVER_URL` | URL del backend de Anote |

## Configuración del Backend

Copia `packages/backend/.env.example` a `packages/backend/.env` y completa:

```bash
# Proveedores de LLM
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...

# Base de Datos
DB_HOST=localhost
DB_NAME=anote
DB_USER=anote
DB_PASSWORD=anote

# Autenticación
JWT_SECRET_KEY=tu-clave-secreta

# Pagos (opcional)
STRIPE_SECRET_KEY=sk_...
```
