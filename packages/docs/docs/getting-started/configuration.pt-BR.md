# Configuração

## Configuração do CLI

A configuração é armazenada em `~/.anote/config.json`:

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

Gerencie via:

```bash
anote config set model claude-opus-4-8
anote config get model
anote config list
```

## Variáveis de Ambiente

Todas as configurações podem ser sobrescritas com variáveis de ambiente:

| Variável | Propósito |
|---|---|
| `ANTHROPIC_API_KEY` | Chave da API da Anthropic |
| `OPENAI_API_KEY` | Chave da API da OpenAI |
| `GEMINI_API_KEY` | Chave da API do Google Gemini |
| `ANOTE_MODEL` | Modelo padrão |
| `ANOTE_SERVER_URL` | URL do backend do Anote |

## Configuração do Backend

Copie `packages/backend/.env.example` para `packages/backend/.env` e preencha:

```bash
# Provedores de LLM
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...

# Banco de Dados
DB_HOST=localhost
DB_NAME=anote
DB_USER=anote
DB_PASSWORD=anote

# Autenticação
JWT_SECRET_KEY=your-secret-key

# Pagamentos (opcional)
STRIPE_SECRET_KEY=sk_...
```
