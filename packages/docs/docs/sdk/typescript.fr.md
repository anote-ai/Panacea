# SDK TypeScript

`@anote-ai/sdk` est un client TypeScript/JavaScript typé pour l'API REST d'Anote. Utilisez-le lorsque vous souhaitez appeler Anote de manière programmatique — depuis un script, un service backend ou votre propre application — au lieu de passer par l'interface en ligne de commande ou l'application web.

!!! note "Communication avec un backend local"
    Par défaut, le client pointe vers `https://api.anote.ai`. Si vous exécutez le backend depuis ce dépôt localement (`docker compose up`, ou `make dev-backend`), passez `baseUrl: "http://localhost:5050"` (ou `:5000` si vous n'utilisez pas la substitution de port) — voir [Premiers pas → Configuration](../getting-started/configuration.md).

## Ce dont vous aurez besoin

- Node.js 18+
- Un compte Anote (inscrivez-vous via `POST /auth/register` ou la page d'inscription de l'application web)
- Une clé API (Étape 2 ci-dessous)

## 1. Installer

```bash
npm install @anote-ai/sdk
```

## 2. Obtenir une clé API

Il n'y a pas encore d'interface de paramètres pour les clés API, donc créez-en une directement contre le backend. Connectez-vous d'abord pour obtenir un JWT, puis utilisez-le pour créer une clé :

```bash
# Connectez-vous pour obtenir un JWT
curl -X POST http://localhost:5050/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "you@example.com", "password": "..."}'
# → { "access_token": "eyJ..." }

# Utilisez le JWT pour créer une clé API
curl -X POST http://localhost:5050/api/user/api-keys \
  -H "Authorization: Bearer eyJ..."
# → { "key": "ak-..." }
```

Sauvegardez cette valeur `ak-...` — elle n'est retournée qu'une seule fois, au moment de la création.

## 3. Initialiser le client

```ts
import { AnoteClient } from "@anote-ai/sdk";

const client = new AnoteClient({
  apiKey: "ak-...",
  baseUrl: "http://localhost:5050", // omettez pour utiliser https://api.anote.ai
});
```

`apiKey` est la seule option requise. Ne laissez pas `baseUrl` lorsque vous êtes pointé vers l'API de production.

## 4. Envoyer votre premier message

```ts
const { result, usage } = await client.chat("Expliquez ce code");

console.log(result);
console.log(`Utilisé ${usage.inputTokens} tokens d'entrée / ${usage.outputTokens} tokens de sortie`);
```

`chat()` est l'appel non en streaming — il attend la réponse complète, ce qui est ce que vous voulez pour le scripting et l'automatisation. Passez `cwd`, `model` ou `tools` dans le deuxième argument pour définir le répertoire de travail, choisir un modèle ou restreindre les outils que l'IA peut utiliser :

```ts
await client.chat("Listez les TODOs dans ce fichier", {
  cwd: "/path/to/project",
  model: "claude-sonnet-4-6",
  tools: ["Read", "Grep"],
});
```

## Tâches courantes

**Lister et inspecter les sessions passées**

```ts
const sessions = await client.listSessions();
const { history } = await client.getSessionMessages(sessions[0].sessionId);
```

**Rechercher dans l'historique des sessions**

```ts
const { results } = await client.search("logique d'authentification");
```

**Vérifier votre utilisation et votre quota**

```ts
const usage = await client.getUsage();
console.log(`${usage.remaining.requests} requêtes restantes ce mois-ci`);
```

**Partager une session sous forme de lien en lecture seule**

```ts
const { shareUrl } = await client.shareSession(sessions[0].sessionId);
```

**Gérer les erreurs**

Chaque réponse non-2xx lance `AnoteError`, qui contient le statut HTTP et le corps de réponse analysé :

```ts
import { AnoteClient, AnoteError } from "@anote-ai/sdk";

try {
  await client.chat("...");
} catch (err) {
  if (err instanceof AnoteError) {
    console.error(err.status, err.message); // par exemple 429, "Quota mensuel dépassé"
  }
}
```

**Vérifier la disponibilité du serveur (aucune authentification requise)**

```ts
const health = await client.health();
```

## Référence API

### `new AnoteClient(options)`

| Option | Type | Requis | Description |
|---|---|---|---|
| `apiKey` | `string` | ✓ | Clé API de l'Étape 2, commence par `ak-` |
| `baseUrl` | `string` | | URL du serveur (par défaut : `https://api.anote.ai`) |

### Méthodes

| Méthode | Description |
|--------|-------------|
| `chat(message, options?)` | Envoyer un message, obtenir une réponse complète de l'IA |
| `listSessions()` | Lister toutes les sessions de chat |
| `getSessionMessages(id)` | Obtenir l'historique des messages pour une session |
| `deleteSession(id)` | Supprimer une session |
| `shareSession(id)` | Créer un lien partageable en lecture seule |
| `search(query, limit?)` | Recherche en texte intégral dans les sessions |
| `getUsage()` | Utilisation du mois en cours + quota |
| `health()` | Vérification de la disponibilité du serveur (aucune authentification nécessaire) |

## Étapes suivantes

- [Aperçu de l'API Backend](../api/overview.md) — les points de terminaison REST sous ce SDK
- [Aperçu de l'CLI](../cli/overview.md) — pour une utilisation interactive/terminal au lieu du scripting
