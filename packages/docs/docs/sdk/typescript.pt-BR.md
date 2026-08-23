# SDK TypeScript

`@anote-ai/sdk` é um cliente tipado TypeScript/JavaScript para a API REST do Anote. Use-o quando quiser chamar o Anote programaticamente — de um script, um serviço de backend ou seu próprio aplicativo — em vez de passar pela CLI ou pelo aplicativo web.

!!! note "Conectando a um backend local"
    Por padrão, o cliente aponta para `https://api.anote.ai`. Se você estiver executando o backend deste repositório localmente (`docker compose up` ou `make dev-backend`), passe `baseUrl: "http://localhost:5050"` (ou `:5000` se você não estiver usando a sobreposição de porta) — veja [Introdução → Configuração](../getting-started/configuration.md).

## O que você vai precisar

- Node.js 18+
- Uma conta Anote (registre-se via `POST /auth/register` ou pela página de Registro do aplicativo web)
- Uma chave de API (Passo 2 abaixo)

## 1. Instalar

```bash
npm install @anote-ai/sdk
```

## 2. Obter uma chave de API

Ainda não há uma interface de configurações para chaves de API, então crie uma diretamente contra o backend. Primeiro, faça login para obter um JWT, depois use-o para criar uma chave:

```bash
# Faça login para obter um JWT
curl -X POST http://localhost:5050/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "you@example.com", "password": "..."}'
# → { "access_token": "eyJ..." }

# Use o JWT para criar uma chave de API
curl -X POST http://localhost:5050/api/user/api-keys \
  -H "Authorization: Bearer eyJ..."
# → { "key": "ak-..." }
```

Salve esse valor `ak-...` — ele é retornado apenas uma vez, no momento da criação.

## 3. Inicializar o cliente

```ts
import { AnoteClient } from "@anote-ai/sdk";

const client = new AnoteClient({
  apiKey: "ak-...",
  baseUrl: "http://localhost:5050", // omita para usar https://api.anote.ai
});
```

`apiKey` é a única opção obrigatória. Deixe `baseUrl` de fora quando você estiver apontando para a API de produção.

## 4. Enviar sua primeira mensagem

```ts
const { result, usage } = await client.chat("Explique este código");

console.log(result);
console.log(`Usou ${usage.inputTokens} tokens de entrada / ${usage.outputTokens} tokens de saída`);
```

`chat()` é a chamada não streaming — ela espera pela resposta completa, que é o que você deseja para scripts e automação. Passe `cwd`, `model` ou `tools` no segundo argumento para definir o diretório de trabalho, escolher um modelo ou restringir quais ferramentas a IA pode usar:

```ts
await client.chat("Liste os TODOs neste arquivo", {
  cwd: "/path/to/project",
  model: "claude-sonnet-4-6",
  tools: ["Read", "Grep"],
});
```

## Tarefas comuns

**Listar e inspecionar sessões passadas**

```ts
const sessions = await client.listSessions();
const { history } = await client.getSessionMessages(sessions[0].sessionId);
```

**Pesquisar no histórico de sessões**

```ts
const { results } = await client.search("lógica de autenticação");
```

**Verificar seu uso e cota**

```ts
const usage = await client.getUsage();
console.log(`${usage.remaining.requests} requisições restantes este mês`);
```

**Compartilhar uma sessão como um link somente leitura**

```ts
const { shareUrl } = await client.shareSession(sessions[0].sessionId);
```

**Tratar erros**

Toda resposta não 2xx lança `AnoteError`, que carrega o status HTTP e o corpo da resposta analisado:

```ts
import { AnoteClient, AnoteError } from "@anote-ai/sdk";

try {
  await client.chat("...");
} catch (err) {
  if (err instanceof AnoteError) {
    console.error(err.status, err.message); // e.g. 429, "Cota mensal excedida"
  }
}
```

**Verificar a disponibilidade do servidor (sem autenticação necessária)**

```ts
const health = await client.health();
```

## Referência da API

### `new AnoteClient(options)`

| Opção | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `apiKey` | `string` | ✓ | Chave de API do Passo 2, começa com `ak-` |
| `baseUrl` | `string` | | URL do servidor (padrão: `https://api.anote.ai`) |

### Métodos

| Método | Descrição |
|--------|-------------|
| `chat(message, options?)` | Enviar uma mensagem, obter uma resposta completa da IA |
| `listSessions()` | Listar todas as sessões de chat |
| `getSessionMessages(id)` | Obter o histórico de mensagens de uma sessão |
| `deleteSession(id)` | Deletar uma sessão |
| `shareSession(id)` | Criar um link compartilhável somente leitura |
| `search(query, limit?)` | Pesquisa de texto completo em sessões |
| `getUsage()` | Uso atual do mês + cota |
| `health()` | Verificação de disponibilidade do servidor (sem autenticação necessária) |

## Próximos passos

- [Visão Geral da API de Backend](../api/overview.md) — os endpoints REST por trás deste SDK
- [Visão Geral da CLI](../cli/overview.md) — para uso interativo/terminal em vez de scripting
