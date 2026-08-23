# TypeScript SDK

`@anote-ai/sdk` ist ein typisierter TypeScript/JavaScript-Client für die Anote REST API. Verwenden Sie ihn, wenn Sie Anote programmgesteuert aufrufen möchten – von einem Skript, einem Backend-Dienst oder Ihrer eigenen App – anstatt über die CLI oder die Webanwendung zu gehen.

!!! note "Kommunikation mit einem lokalen Backend"
    Standardmäßig zeigt der Client auf `https://api.anote.ai`. Wenn Sie das Backend lokal aus diesem Repository ausführen (`docker compose up` oder `make dev-backend`), übergeben Sie `baseUrl: "http://localhost:5050"` (oder `:5000`, wenn Sie die Portüberschreibung nicht verwenden) – siehe [Erste Schritte → Konfiguration](../getting-started/configuration.md).

## Was Sie benötigen

- Node.js 18+
- Ein Anote-Konto (registrieren Sie sich über `POST /auth/register` oder die Registrierungsseite der Webanwendung)
- Ein API-Schlüssel (Schritt 2 unten)

## 1. Installieren

```bash
npm install @anote-ai/sdk
```

## 2. API-Schlüssel erhalten

Es gibt noch keine Einstellungen-Benutzeroberfläche für API-Schlüssel, also erstellen Sie einen direkt gegen das Backend. Melden Sie sich zuerst an, um ein JWT zu erhalten, und verwenden Sie es dann, um einen Schlüssel zu erstellen:

```bash
# Melden Sie sich an, um ein JWT zu erhalten
curl -X POST http://localhost:5050/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "you@example.com", "password": "..."}'
# → { "access_token": "eyJ..." }

# Verwenden Sie das JWT, um einen API-Schlüssel zu erstellen
curl -X POST http://localhost:5050/api/user/api-keys \
  -H "Authorization: Bearer eyJ..."
# → { "key": "ak-..." }
```

Speichern Sie diesen `ak-...` Wert – er wird nur einmal, zum Zeitpunkt der Erstellung, zurückgegeben.

## 3. Den Client initialisieren

```ts
import { AnoteClient } from "@anote-ai/sdk";

const client = new AnoteClient({
  apiKey: "ak-...",
  baseUrl: "http://localhost:5050", // weglassen, um https://api.anote.ai zu verwenden
});
```

`apiKey` ist die einzige erforderliche Option. Lassen Sie `baseUrl` weg, wenn Sie auf die Produktions-API zeigen.

## 4. Ihre erste Nachricht senden

```ts
const { result, usage } = await client.chat("Erklären Sie diesen Code");

console.log(result);
console.log(`Verwendete ${usage.inputTokens} Eingabe- / ${usage.outputTokens} Ausgabe-Token`);
```

`chat()` ist der nicht-streamende Aufruf – er wartet auf die vollständige Antwort, was Sie für Skripting und Automatisierung möchten. Übergeben Sie `cwd`, `model` oder `tools` im zweiten Argument, um das Arbeitsverzeichnis festzulegen, ein Modell auszuwählen oder einzuschränken, welche Tools die KI verwenden darf:

```ts
await client.chat("Liste TODOs in dieser Datei", {
  cwd: "/path/to/project",
  model: "claude-sonnet-4-6",
  tools: ["Read", "Grep"],
});
```

## Häufige Aufgaben

**Liste und inspiziere vergangene Sitzungen**

```ts
const sessions = await client.listSessions();
const { history } = await client.getSessionMessages(sessions[0].sessionId);
```

**Durchsuche die Sitzungsverlauf**

```ts
const { results } = await client.search("Authentifizierungslogik");
```

**Überprüfen Sie Ihre Nutzung und Ihr Kontingent**

```ts
const usage = await client.getUsage();
console.log(`${usage.remaining.requests} Anfragen verbleibend in diesem Monat`);
```

**Teilen Sie eine Sitzung als schreibgeschützten Link**

```ts
const { shareUrl } = await client.shareSession(sessions[0].sessionId);
```

**Fehler behandeln**

Jede Antwort, die nicht 2xx ist, wirft `AnoteError`, der den HTTP-Status und den analysierten Antwortkörper enthält:

```ts
import { AnoteClient, AnoteError } from "@anote-ai/sdk";

try {
  await client.chat("...");
} catch (err) {
  if (err instanceof AnoteError) {
    console.error(err.status, err.message); // z.B. 429, "Monatliches Kontingent überschritten"
  }
}
```

**Überprüfen Sie die Serververfügbarkeit (keine Authentifizierung erforderlich)**

```ts
const health = await client.health();
```

## API-Referenz

### `new AnoteClient(options)`

| Option | Typ | Erforderlich | Beschreibung |
|---|---|---|---|
| `apiKey` | `string` | ✓ | API-Schlüssel aus Schritt 2, beginnt mit `ak-` |
| `baseUrl` | `string` | | Server-URL (Standard: `https://api.anote.ai`) |

### Methoden

| Methode | Beschreibung |
|--------|-------------|
| `chat(message, options?)` | Senden Sie eine Nachricht, erhalten Sie eine vollständige KI-Antwort |
| `listSessions()` | Listet alle Chatsitzungen auf |
| `getSessionMessages(id)` | Holt die Nachrichtenhistorie für eine Sitzung |
| `deleteSession(id)` | Löscht eine Sitzung |
| `shareSession(id)` | Erstellt einen teilbaren schreibgeschützten Link |
| `search(query, limit?)` | Volltextsuche über Sitzungen |
| `getUsage()` | Aktuelle Monatsnutzung + Kontingent |
| `health()` | Überprüfung der Serververfügbarkeit (keine Authentifizierung erforderlich) |

## Nächste Schritte

- [Backend API Übersicht](../api/overview.md) — die REST-Endpunkte unter diesem SDK
- [CLI Übersicht](../cli/overview.md) — für interaktive/Terminal-Nutzung anstelle von Skripting
