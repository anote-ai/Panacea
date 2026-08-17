# Resumen

**Anote AI** es un asistente de codificación con IA unificado y una plataforma de chat privada. Lee tu codebase, edita archivos, ejecuta comandos, revisa pull requests y responde preguntas sobre tus documentos — disponible en tu terminal, IDE, navegador, aplicación de escritorio y teléfono.

## Primeros pasos

Anote funciona en varias superficies: la CLI, VS Code, la web, escritorio y móvil. Elige una a continuación para empezar. La mayoría de las superficies se comunican con el backend de Anote alojado o con tu propia instancia autoalojada (consulta [Configuración](getting-started/configuration.md)).

=== "CLI"

    La CLI completa para trabajar con Anote directamente en tu terminal. Haz preguntas, corrige errores, revisa pull requests y busca en tu codebase sin salir de la shell.

    ```bash
    npm install -g @anote-ai/anote
    ```

    Requiere Node.js 18 o posterior. Luego, en cualquier proyecto:

    ```bash
    cd your-project
    anote init
    anote ask "explain this codebase"
    ```

    `anote init` te guía en la configuración de tu clave API y proveedor de LLM preferido.

    [Continuar con la Guía rápida →](getting-started/quickstart.md)

=== "VS Code"

    La extensión de VS Code añade una barra lateral de chat, revisión de diffs en línea y respuestas en streaming directamente en tu editor.

    Busca **"Anote"** en el marketplace de extensiones de VS Code, o instálala con:

    ```bash
    code --install-extension anote-ai.anote-ai-coding
    ```

    [Resumen de la extensión VS Code →](vscode/overview.md)

=== "Aplicación Web"

    Una interfaz de chat estilo ChatGPT en el navegador, con carga de documentos y preguntas y respuestas basadas en RAG. Aloja tu propia instancia con Docker Compose:

    ```bash
    git clone https://github.com/anote-ai/Panacea
    cd Panacea
    cp packages/backend/.env.example packages/backend/.env
    # Edita .env con tus claves API
    docker compose up
    ```

    Frontend: `http://localhost:3000` · Backend: `http://localhost:5000`

    [Resumen de la aplicación Web →](web/overview.md)

=== "Escritorio"

    Una aplicación Electron privada y capaz de funcionar sin conexión. Todos los datos permanecen en tu máquina, y funciona con modelos Ollama locales cuando no quieres depender de un proveedor alojado.

    Descarga la última versión desde [GitHub Releases](https://github.com/anote-ai/Panacea/releases) — disponible para **macOS** (DMG), **Windows** (instalador) y **Linux** (AppImage/DEB/RPM).

    [Resumen de la aplicación de Escritorio →](desktop/overview.md)

=== "Móvil"

    Un cliente de chat nativo para iOS y Android, construido con Expo.

    ```bash
    cd packages/mobile
    npm install
    npx expo start
    ```

    Escanea el código QR con la app Expo Go, o ejecútalo en un simulador.

    [Resumen de la aplicación Móvil →](mobile/overview.md)

## Qué puedes hacer

??? abstract "Hacer preguntas sobre tu codebase"

    ```bash
    anote ask "how does the authentication middleware work?"
    anote ask --file src/auth.ts "explain this file"
    anote ask --compare               # comparación lado a lado entre varios modelos
    cat src/handler.py | anote ask "what could go wrong here?"
    ```

??? bug "Corregir errores automáticamente"

    `anote fix --loop` itera sobre tu suite de pruebas — hasta `--max-iterations` rondas — hasta que pase, o corrige un solo archivo con `--file`.

    ```bash
    anote fix --loop --max-iterations 5
    ```

??? example "Revisar pull requests"

    ```bash
    anote review --pr 42
    ```

    Revisiones de errores, problemas de seguridad y calidad — localmente sobre un directorio/archivo, o publicadas directamente en un PR de GitHub.

??? search "Buscar en tu codebase semánticamente"

    ```bash
    anote index              # construir un índice TF-IDF (una vez, luego mantenido al día)
    anote search "JWT token validation"
    ```

??? question "Chatear y preguntar sobre tus documentos"

    Sube documentos en la [aplicación Web](web/overview.md) o la [aplicación de Escritorio](desktop/overview.md) y hazles preguntas — basado en RAG mediante `POST /api/documents/{id}/ask`.

??? tip "Auditar seguridad y rendimiento"

    ```bash
    anote security --severity high --fix
    anote perf --focus "database,bundle" --fix
    ```

??? note "Generar changelogs y documentación, o ejecutar migraciones"

    ```bash
    anote changelog --since v1.2.0
    anote docs src/api.ts --style jsdoc
    anote migrate --from "React 17" --to "React 18"
    ```

??? info "Comprobar tu configuración"

    ```bash
    anote doctor
    ```

    Comprueba Node.js ≥ 18, `ANTHROPIC_API_KEY`, `.anote.json`, `CLAW.md` y git.

## Usa Anote en cualquier lugar

| Quiero... | Mejor opción |
|---|---|
| Trabajar desde mi terminal | [CLI](cli/overview.md) |
| Ayuda de IA directamente en mi editor | [Extensión VS Code](vscode/overview.md) |
| Chatear con documentos en un navegador | [Aplicación Web](web/overview.md) |
| Mantener todo privado y sin conexión | [Aplicación de Escritorio](desktop/overview.md) — funciona con modelos Ollama locales |
| Chatear desde mi teléfono | [Aplicación Móvil](mobile/overview.md) |
| Llamar a Anote desde mi propio código o scripts | [SDK de TypeScript](sdk/typescript.md) o [SDK de Python](sdk/python.md) |
| Integrarme directamente con la API REST | [API del Backend](api/overview.md) |
| Automatizar la revisión de PR o comprobaciones de CI | [CLI: `anote review --pr`](cli/commands.md#anote-review) |

## Proveedores de LLM compatibles

- **Anthropic** — Claude (`claude-opus-4-8`, `claude-sonnet-4-6`, `claude-haiku-4-5`)
- **OpenAI** — GPT-4o, GPT-4o-mini
- **Google** — Gemini 2.0 Flash, Gemini 1.5 Pro
- **Ollama** — cualquier modelo local (Llama 3, Mistral, etc.)
- **xAI** — Grok

## Próximos pasos

- [Guía rápida](getting-started/quickstart.md) — init, ask, fix, index, review y changelog en orden
- [Cómo funciona Panacea](core-concepts/how-it-works.md) — el bucle agéntico, las herramientas y el streaming
- [Modos de permiso](use-panacea/permission-modes.md) — controla qué puede hacer el agente sin preguntar
- [Flujos de trabajo comunes](use-panacea/common-workflows.md) — patrones paso a paso para tareas cotidianas
- [Configuración](getting-started/configuration.md) — claves API, configuración de proveedor y `~/.anote/config.json`
- [Comandos CLI](cli/commands.md) — la referencia completa de comandos
- [API del Backend](api/overview.md) — los endpoints REST que impulsan cada superficie
- [Arquitectura](development/architecture.md) — cómo encajan el monorepo y el backend
- [Contribuir](development/contributing.md) — configura el repositorio para desarrollo local
