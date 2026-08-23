# Modos de Permiso

Panacea tiene tres modos de permiso, que controlan si el agente pregunta antes de escribir archivos o ejecutar comandos.

| Modo | Comportamiento |
|---|---|
| `default` | Confirma antes de editar archivos o ejecutar comandos que no son de solo lectura |
| `acceptEdits` | Acepta automáticamente las ediciones de archivos sin preguntar |
| `bypassPermissions` | Ejecuta todo sin confirmación — usar con cuidado |

Configúralo globalmente o por proyecto:

```bash
anote config set permissionMode acceptEdits
```

o en `.anote.json`:

```json
{ "permissionMode": "acceptEdits" }
```

## Sobrescrituras por comando

La mayoría de los comandos no requieren que toques la configuración global — toman sus propias banderas para la misma idea:

| Bandera | Disponible en | Efecto |
|---|---|---|
| `--auto` | `fix`, `refactor` | Acepta automáticamente las ediciones solo para esta ejecución |
| `--dry-run` | `fix`, `docs`, `migrate`, `security`, `perf`, `refactor`, `generate`, `changelog`, `commit`, `review` | Muestra lo que sucedería sin escribir nada |
| `--no-edit` | `ask` | Solo lectura — el agente no puede modificar archivos incluso si quiere |
| `--yes` | `init` | Omite los mensajes interactivos, acepta los valores predeterminados |

`anote fix --loop` implica `acceptEdits` automáticamente, ya que necesita seguir editando a través de iteraciones sin detenerse a preguntar cada vez.

## Hooks como una capa de política

Para cualquier cosa más específica que "preguntar vs. no preguntar" — como bloquear llamadas de `Bash` que toquen un cierto camino — usa un hook `preToolUse` en su lugar. Consulta [Extender Panacea](../core-concepts/extend.md).

## Próximos pasos

- [Cómo funciona Panacea](../core-concepts/how-it-works.md) — el bucle del agente que estos modos controlan
- [Explorar el directorio .anote](../core-concepts/anote-directory.md) — donde vive `permissionMode` en la configuración
