# Cómo funciona Panacea

Panacea ejecuta un **bucle agentic**: lee tu solicitud, decide qué herramientas llamar, las ejecuta, lee los resultados y repite — transmitiendo su razonamiento y ediciones de vuelta a ti — hasta que la tarea esté completa o alcance un límite de turnos.

## Las herramientas

Por defecto, el agente de Panacea puede llamar a:

| Herramienta | Propósito |
|---|---|
| `Read` | Leer un archivo |
| `Write` | Crear o sobrescribir un archivo |
| `Edit` | Hacer un cambio específico en un archivo |
| `Bash` | Ejecutar un comando de shell |
| `Glob` | Encontrar archivos por patrón |
| `Grep` | Buscar contenido en archivos |

Algunos comandos reducen esta lista — `anote review` y `anote diff`, por ejemplo, solo permiten `Read`, `Glob`, `Grep` y `Bash`, ya que una revisión no debería escribir archivos.

## Turnos y compactación

Cada par de llamada/respuesta de herramienta cuenta como un turno. El agente se detiene después de `maxTurns` (por defecto 30, configurable a través de `anote config set maxTurns <n>` o `.anote.json`). Las sesiones largas se compactan después de `compactAfterMessages` (por defecto 40) para mantener la ventana de contexto manejable.

## Transmisión

Cada superficie — CLI, VS Code, Web, Escritorio — se comunica con el mismo punto final de backend (`POST /api/chat/stream`), que transmite la respuesta del modelo y la actividad de la herramienta a través de SSE a medida que sucede. Ves lecturas de archivos, ediciones y salida de comandos en vivo, no solo la respuesta final.

## Múltiples proveedores

El bucle del agente no está atado a un solo modelo. `anote ask --compare` ejecuta la misma solicitud en múltiples modelos uno al lado del otro, y `--model` en la mayoría de los comandos acepta cualquier proveedor configurado (`claude-sonnet-4-6`, `gpt-4.1`, `gemini-2.5-pro`, o un `ollama/<model>` local).

## Próximos pasos

- [Modos de permiso](../use-panacea/permission-modes.md) — controla si el agente pregunta antes de editar o ejecutar comandos
- [Extender Panacea](extend.md) — CLAW.md y hooks
- [Comandos de CLI](../cli/commands.md) — la referencia completa de comandos
