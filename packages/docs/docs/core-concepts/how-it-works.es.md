# Cómo funciona Panacea

Panacea ejecuta un **bucle agéntico**: lee tu prompt, decide qué herramientas llamar, las ejecuta, lee los resultados y repite — transmitiéndote su razonamiento y ediciones en streaming — hasta que la tarea esté completa o alcance un límite de turnos.

## Las herramientas

Por defecto, el agente de Panacea puede llamar a:

| Herramienta | Propósito |
|---|---|
| `Read` | Leer un archivo |
| `Write` | Crear o sobrescribir un archivo |
| `Edit` | Hacer un cambio específico en un archivo |
| `Bash` | Ejecutar un comando de shell |
| `Glob` | Encontrar archivos por patrón |
| `Grep` | Buscar en el contenido de archivos |

Algunos comandos restringen esta lista — `anote review` y `anote diff`, por ejemplo, solo permiten `Read`, `Glob`, `Grep` y `Bash`, ya que una revisión no debería escribir archivos.

## Turnos y compactación

Cada par de llamada a herramienta/respuesta cuenta como un turno. El agente se detiene después de `maxTurns` (30 por defecto, configurable mediante `anote config set maxTurns <n>` o `.anote.json`). Las sesiones largas se compactan después de `compactAfterMessages` (40 por defecto) para mantener manejable la ventana de contexto.

## Streaming

Cada superficie — CLI, VS Code, Web, Escritorio — se comunica con el mismo endpoint del backend (`POST /api/chat/stream`), que transmite en streaming la respuesta del modelo y la actividad de las herramientas vía SSE a medida que ocurre. Ves las lecturas de archivos, ediciones y salida de comandos en vivo, no solo la respuesta final.

## Multi-proveedor

El bucle del agente no está atado a un solo modelo. `anote ask --compare` ejecuta el mismo prompt en varios modelos en paralelo, y `--model` en la mayoría de los comandos acepta cualquier proveedor configurado (`claude-sonnet-4-6`, `gpt-4.1`, `gemini-2.5-pro`, o un `ollama/<model>` local).

## Próximos pasos

- [Modos de permiso](../use-panacea/permission-modes.md) — controla si el agente pregunta antes de editar archivos o ejecutar comandos
- [Extender Panacea](extend.md) — CLAW.md y hooks
- [Comandos CLI](../cli/commands.md) — la referencia completa de comandos
