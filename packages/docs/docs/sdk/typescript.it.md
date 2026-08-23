# TypeScript SDK

`@anote-ai/sdk` è un client tipizzato TypeScript/JavaScript per l'API REST di Anote. Usalo quando desideri chiamare Anote programmaticamente — da uno script, un servizio backend o la tua app — invece di passare attraverso la CLI o l'app web.

!!! note "Parlare con un backend locale"
    Per impostazione predefinita, il client punta a `https://api.anote.ai`. Se stai eseguendo il backend da questo repo localmente (`docker compose up`, o `make dev-backend`), passa `baseUrl: "http://localhost:5050"` (o `:5000` se non stai usando l'override della porta) — vedi [Iniziare → Configurazione](../getting-started/configuration.md).

## Cosa ti servirà

- Node.js 18+
- Un account Anote (registrati tramite `POST /auth/register` o la pagina di registrazione dell'app web)
- Una chiave API (Passo 2 qui sotto)

## 1. Installa

```bash
npm install @anote-ai/sdk
```

## 2. Ottieni una chiave API

Non c'è ancora un'interfaccia UI per le chiavi API, quindi creane una direttamente contro il backend. Prima accedi per ottenere un JWT, poi usalo per creare una chiave:

```bash
# Accedi per ottenere un JWT
curl -X POST http://localhost:5050/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "you@example.com", "password": "..."}'
# → { "access_token": "eyJ..." }

# Usa il JWT per creare una chiave API
curl -X POST http://localhost:5050/api/user/api-keys \
  -H "Authorization: Bearer eyJ..."
# → { "key": "ak-..." }
```

Salva quel valore `ak-...` — viene restituito solo una volta, al momento della creazione.

## 3. Inizializza il client

```ts
import { AnoteClient } from "@anote-ai/sdk";

const client = new AnoteClient({
  apiKey: "ak-...",
  baseUrl: "http://localhost:5050", // ometti per usare https://api.anote.ai
});
```

`apiKey` è l'unica opzione richiesta. Lascia fuori `baseUrl` quando sei puntato all'API di produzione.

## 4. Invia il tuo primo messaggio

```ts
const { result, usage } = await client.chat("Spiega questo codice");

console.log(result);
console.log(`Usati ${usage.inputTokens} token di input / ${usage.outputTokens} token di output`);
```

`chat()` è la chiamata non streaming — aspetta la risposta completa, che è ciò che desideri per scripting e automazione. Passa `cwd`, `model` o `tools` nel secondo argomento per definire la directory di lavoro, scegliere un modello o limitare quali strumenti l'AI può utilizzare:

```ts
await client.chat("Elenca i TODO in questo file", {
  cwd: "/path/to/project",
  model: "claude-sonnet-4-6",
  tools: ["Read", "Grep"],
});
```

## Attività comuni

**Elenca e ispeziona le sessioni passate**

```ts
const sessions = await client.listSessions();
const { history } = await client.getSessionMessages(sessions[0].sessionId);
```

**Cerca nella cronologia delle sessioni**

```ts
const { results } = await client.search("logica di autenticazione");
```

**Controlla il tuo utilizzo e la tua quota**

```ts
const usage = await client.getUsage();
console.log(`${usage.remaining.requests} richieste rimanenti questo mese`);
```

**Condividi una sessione come link di sola lettura**

```ts
const { shareUrl } = await client.shareSession(sessions[0].sessionId);
```

**Gestisci gli errori**

Ogni risposta non 2xx genera `AnoteError`, che porta lo stato HTTP e il corpo della risposta analizzato:

```ts
import { AnoteClient, AnoteError } from "@anote-ai/sdk";

try {
  await client.chat("...");
} catch (err) {
  if (err instanceof AnoteError) {
    console.error(err.status, err.message); // e.g. 429, "Quota mensile superata"
  }
}
```

**Controlla la disponibilità del server (nessuna autenticazione richiesta)**

```ts
const health = await client.health();
```

## Riferimento API

### `new AnoteClient(options)`

| Opzione | Tipo | Richiesta | Descrizione |
|---|---|---|---|
| `apiKey` | `string` | ✓ | Chiave API dal Passo 2, inizia con `ak-` |
| `baseUrl` | `string` | | URL del server (predefinito: `https://api.anote.ai`) |

### Metodi

| Metodo | Descrizione |
|--------|-------------|
| `chat(message, options?)` | Invia un messaggio, ottieni una risposta completa dall'AI |
| `listSessions()` | Elenca tutte le sessioni di chat |
| `getSessionMessages(id)` | Ottieni la cronologia dei messaggi per una sessione |
| `deleteSession(id)` | Elimina una sessione |
| `shareSession(id)` | Crea un link condivisibile di sola lettura |
| `search(query, limit?)` | Ricerca full-text nelle sessioni |
| `getUsage()` | Utilizzo corrente del mese + quota |
| `health()` | Controllo della disponibilità del server (nessuna autenticazione necessaria) |

## Prossimi passi

- [Panoramica dell'API Backend](../api/overview.md) — gli endpoint REST sottostanti a questo SDK
- [Panoramica della CLI](../cli/overview.md) — per uso interattivo/terminal invece di scripting
