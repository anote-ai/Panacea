# SDK de TypeScript

`@anote-ai/sdk` es un cliente tipado de TypeScript/JavaScript para la API REST de Anote. Úsalo cuando desees llamar a Anote programáticamente — desde un script, un servicio backend o tu propia aplicación — en lugar de pasar por la CLI o la aplicación web.

!!! note "Hablando con un backend local"
    Por defecto, el cliente apunta a `https://api.anote.ai`. Si estás ejecutando el backend desde este repositorio localmente (`docker compose up`, o `make dev-backend`), pasa `baseUrl: "http://localhost:5050"` (o `:5000` si no estás usando la sobreescritura de puerto) — consulta [Introducción → Configuración](../getting-started/configuration.md).

## Lo que necesitarás

- Node.js 18+
- Una cuenta de Anote (regístrate a través de `POST /auth/register` o la página de Registro de la aplicación web)
- Una clave API (Paso 2 a continuación)

## 1. Instalar

```bash
npm install @anote-ai/sdk
```

## 2. Obtener una clave API

Aún no hay una interfaz de configuración para claves API, así que crea una directamente contra el backend. Primero inicia sesión para obtener un JWT, luego úsalo para crear una clave:

```bash
# Inicia sesión para obtener un JWT
curl -X POST http://localhost:5050/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "you@example.com", "password": "..."}'
# → { "access_token": "eyJ..." }

# Usa el JWT para crear una clave API
curl -X POST http://localhost:5050/api/user/api-keys \
  -H "Authorization: Bearer eyJ..."
# → { "key": "ak-..." }
```

Guarda ese valor `ak-...` — solo se devuelve una vez, en el momento de la creación.

## 3. Inicializar el cliente

```ts
import { AnoteClient } from "@anote-ai/sdk";

const client = new AnoteClient({
  apiKey: "ak-...",
  baseUrl: "http://localhost:5050", // omite para usar https://api.anote.ai
});
```

`apiKey` es la única opción requerida. Omite `baseUrl` cuando estés apuntando a la API de producción.

## 4. Envía tu primer mensaje

```ts
const { result, usage } = await client.chat("Explica esta base de código");

console.log(result);
console.log(`Usados ${usage.inputTokens} tokens de entrada / ${usage.outputTokens} tokens de salida`);
```

`chat()` es la llamada no en streaming — espera la respuesta completa, que es lo que deseas para scripting y automatización. Pasa `cwd`, `model` o `tools` en el segundo argumento para definir el directorio de trabajo, elegir un modelo o restringir qué herramientas puede usar la IA:

```ts
await client.chat("Lista los TODOs en este archivo", {
  cwd: "/path/to/project",
  model: "claude-sonnet-4-6",
  tools: ["Read", "Grep"],
});
```

## Tareas comunes

**Listar e inspeccionar sesiones pasadas**

```ts
const sessions = await client.listSessions();
const { history } = await client.getSessionMessages(sessions[0].sessionId);
```

**Buscar en el historial de sesiones**

```ts
const { results } = await client.search("lógica de autenticación");
```

**Verifica tu uso y cuota**

```ts
const usage = await client.getUsage();
console.log(`${usage.remaining.requests} solicitudes restantes este mes`);
```

**Compartir una sesión como un enlace de solo lectura**

```ts
const { shareUrl } = await client.shareSession(sessions[0].sessionId);
```

**Manejar errores**

Cada respuesta que no sea 2xx lanza `AnoteError`, que lleva el estado HTTP y el cuerpo de respuesta analizado:

```ts
import { AnoteClient, AnoteError } from "@anote-ai/sdk";

try {
  await client.chat("...");
} catch (err) {
  if (err instanceof AnoteError) {
    console.error(err.status, err.message); // por ejemplo, 429, "Cuota mensual excedida"
  }
}
```

**Verificar la disponibilidad del servidor (sin autenticación requerida)**

```ts
const health = await client.health();
```

## Referencia de la API

### `new AnoteClient(options)`

| Opción | Tipo | Requerido | Descripción |
|---|---|---|---|
| `apiKey` | `string` | ✓ | Clave API del Paso 2, comienza con `ak-` |
| `baseUrl` | `string` | | URL del servidor (por defecto: `https://api.anote.ai`) |

### Métodos

| Método | Descripción |
|--------|-------------|
| `chat(message, options?)` | Envía un mensaje, obtiene una respuesta completa de la IA |
| `listSessions()` | Lista todas las sesiones de chat |
| `getSessionMessages(id)` | Obtiene el historial de mensajes de una sesión |
| `deleteSession(id)` | Elimina una sesión |
| `shareSession(id)` | Crea un enlace de solo lectura compartible |
| `search(query, limit?)` | Búsqueda de texto completo en las sesiones |
| `getUsage()` | Uso actual del mes + cuota |
| `health()` | Verificación de disponibilidad del servidor (sin autenticación necesaria) |

## Próximos pasos

- [Descripción general de la API del backend](../api/overview.md) — los endpoints REST debajo de este SDK
- [Descripción general de la CLI](../cli/overview.md) — para uso interactivo/terminal en lugar de scripting
