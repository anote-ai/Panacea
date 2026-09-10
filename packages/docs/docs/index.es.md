# Descripción general

**Ourogen** es una plataforma unificada de asistente de codificación AI y chatbot privado. Lee tu código, edita archivos, ejecuta comandos, revisa PRs y responde preguntas sobre tus documentos, disponible en tu terminal, IDE, navegador, aplicación de escritorio y teléfono.

## Comenzar

Anote funciona en varias superficies: la CLI, VS Code, la web, escritorio y móvil. Elige una a continuación para comenzar. La mayoría de las superficies se conectan al backend de Anote alojado o a tu propia instancia autoalojada (ver [Configuración](getting-started/configuration.md)).

=== "CLI"

    La CLI completa para trabajar con Anote directamente en tu terminal. Haz preguntas, corrige errores, revisa PRs y busca en tu código sin salir de la terminal.

    ```bash
    npm install -g @anote-ai/anote
    ```

    Requiere Node.js 18 o posterior. Luego, en cualquier proyecto:

    ```bash
    cd tu-proyecto
    anote init
    anote ask "explica esta base de código"
    ```

    `anote init` te guía para configurar tu clave API y proveedor LLM preferido.

    [Continúa con el Inicio Rápido →](getting-started/quickstart.md)

=== "VS Code"

    La extensión de VS Code trae una barra lateral de chat, revisión de diferencias en línea y respuestas en tiempo real directamente en tu editor.

    Busca **"Anote"** en el mercado de extensiones de VS Code, o instala a través de:

    ```bash
    code --install-extension anote-ai.anote-ai-coding
    ```

    [Descripción general de la extensión de VS Code →](vscode/overview.md)

=== "Aplicación web"

    Una interfaz de chat en el navegador estilo ChatGPT con carga de documentos y preguntas y respuestas respaldadas por RAG. Autoalójala con Docker Compose:

    ```bash
    git clone https://github.com/anote-ai/Panacea
    cd Panacea
    cp packages/backend/.env.example packages/backend/.env
    # Edita .env con tus claves API
    docker compose up
    ```

    Frontend: `http://localhost:3000` · Backend: `http://localhost:5000`

    [Descripción general de la aplicación web →](web/overview.md)

=== "Escritorio"

    Una aplicación privada de Electron capaz de funcionar sin conexión. Todos los datos permanecen en tu máquina y funciona con modelos locales de Ollama cuando no deseas llamar a un proveedor alojado.

    Descarga la última versión desde [GitHub Releases](https://github.com/anote-ai/Panacea/releases) — disponible para **macOS** (DMG), **Windows** (instalador) y **Linux** (AppImage/DEB/RPM).

    [Descripción general de la aplicación de escritorio →](desktop/overview.md)

=== "Móvil"

    Un cliente de chat nativo para iOS y Android construido con Expo.

    ```bash
    cd packages/mobile
    npm install
    npx expo start
    ```

    Escanea el código QR con la aplicación Expo Go, o ejecuta en un simulador.

    [Descripción general de la aplicación móvil →](mobile/overview.md)

## Lo que puedes hacer

??? abstract "Haz preguntas sobre tu base de código"

    ```bash
    anote ask "¿cómo funciona el middleware de autenticación?"
    anote ask --file src/auth.ts "explica este archivo"
    anote ask --compare               # lado a lado entre múltiples modelos
    cat src/handler.py | anote ask "¿qué podría salir mal aquí?"
    ```

??? bug "Corrige errores automáticamente"

    `anote fix --loop` itera contra tu suite de pruebas — hasta `--max-iterations` rondas — hasta que pase, o corrige un solo archivo con `--file`.

    ```bash
    anote fix --loop --max-iterations 5
    ```

??? example "Revisa solicitudes de extracción"

    ```bash
    anote review --pr 42
    ```

    Revisa en busca de errores, problemas de seguridad y calidad — localmente contra un directorio/archivo, o publicado directamente a un PR de GitHub.

??? search "Busca en tu base de código semánticamente"

    ```bash
    anote index              # construye un índice TF-IDF (ejecuta una vez, luego mantén actualizado)
    anote search "validación de token JWT"
    ```

??? question "Chatea y haz preguntas y respuestas sobre tus documentos"

    Sube documentos en la [Aplicación web](web/overview.md) o [Aplicación de escritorio](desktop/overview.md) y haz preguntas sobre ellos — respaldado por RAG a través de `POST /api/documents/{id}/ask`.

??? tip "Audita problemas de seguridad y rendimiento"

    ```bash
    anote security --severity high --fix
    anote perf --focus "database,bundle" --fix
    ```

??? note "Genera changelogs y documentación, o ejecuta migraciones"

    ```bash
    anote changelog --since v1.2.0
    anote docs src/api.ts --style jsdoc
    anote migrate --from "React 17" --to "React 18"
    ```

??? info "Verifica tu configuración"

    ```bash
    anote doctor
    ```

    Verifica Node.js ≥ 18, `ANTHROPIC_API_KEY`, `.anote.json`, `CLAW.md` y git.

## Usa Anote en todas partes

| Quiero... | Mejor opción |
|---|---|
| Trabajar desde mi terminal | [CLI](cli/overview.md) |
| Obtener ayuda AI en línea en mi editor | [Extensión de VS Code](vscode/overview.md) |
| Chatear con documentos en un navegador | [Aplicación web](web/overview.md) |
| Mantener todo privado y sin conexión | [Aplicación de escritorio](desktop/overview.md) — funciona con modelos locales de Ollama |
| Chatear desde mi teléfono | [Aplicación móvil](mobile/overview.md) |
| Llamar a Anote desde mi propio código o scripts | [SDK de TypeScript](sdk/typescript.md) o [SDK de Python](sdk/python.md) |
| Integrar directamente contra la API REST | [API de Backend](api/overview.md) |
| Automatizar la revisión de PR o verificaciones de CI | [CLI: `anote review --pr`](cli/commands.md#anote-review) |

## Proveedores de LLM soportados

- **Anthropic** — Claude (`claude-opus-4-8`, `claude-sonnet-4-6`, `claude-haiku-4-5`)
- **OpenAI** — GPT-4o, GPT-4o-mini
- **Google** — Gemini 2.0 Flash, Gemini 1.5 Pro
- **Ollama** — cualquier modelo local (Llama 3, Mistral, etc.)
- **xAI** — Grok

## Próximos pasos

- [Inicio Rápido](getting-started/quickstart.md) — init, ask, fix, index, review y changelog en orden
- [Cómo funciona Panacea](core-concepts/how-it-works.md) — el bucle agente, herramientas y streaming
- [Modos de Permiso](use-panacea/permission-modes.md) — controla lo que el agente puede hacer sin preguntar
- [Flujos de Trabajo Comunes](use-panacea/common-workflows.md) — patrones paso a paso para tareas cotidianas
- [Configuración](getting-started/configuration.md) — claves API, configuración del proveedor y `~/.anote/config.json`
- [Comandos de CLI](cli/commands.md) — la referencia completa de comandos
- [API de Backend](api/overview.md) — los endpoints REST que alimentan cada superficie
- [Arquitectura](development/architecture.md) — cómo se integran el monorepo y el backend
- [Contribuyendo](development/contributing.md) — configura el repositorio para el desarrollo local
