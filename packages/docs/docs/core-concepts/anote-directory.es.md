# Explorar el directorio .anote

El CLI de Panacea lee la configuración desde dos lugares: un archivo por proyecto y uno global.

## Configuración del proyecto

Panacea busca hacia arriba desde tu directorio actual el primer archivo que encuentra, en este orden:

- `.anote.json`
- `.claw.json`
- `anote.config.json`

```json
{
  "model": "claude-sonnet-4-6",
  "permissionMode": "default",
  "maxTurns": 20,
  "compactAfterMessages": 40,
  "hooks": {
    "preToolUse": [],
    "postToolUse": []
  }
}
```

| Clave | Propósito |
|---|---|
| `model` | Modelo predeterminado para este proyecto |
| `permissionMode` | `default`, `acceptEdits`, o `bypassPermissions` — ver [Modos de permiso](../use-panacea/permission-modes.md) |
| `provider` | Anulación explícita del proveedor (generalmente detectado automáticamente desde `model`) |
| `baseUrl` | URL base para puntos finales compatibles con OpenAI, por ejemplo, `http://localhost:11434/v1` para Ollama |
| `maxTurns` | Límite de turnos por sesión |
| `compactAfterMessages` | Cuándo compactar el historial de la sesión |
| `hooks` | Ganchos de shell `preToolUse` / `postToolUse` — ver [Extender Panacea](extend.md) |

`anote init` crea `.anote.json` para ti. `anote config` lo lee y escribe:

```bash
anote config              # mostrar configuración efectiva (global + local)
anote config get model
anote config set model gpt-4.1
anote config path         # imprimir la ruta del archivo de configuración global
anote config edit         # abrir la configuración global en $EDITOR
```

## Configuración global

`~/.anote/config.json` contiene tus valores predeterminados — aplicados siempre que un proyecto no los anule. La configuración del proyecto siempre tiene prioridad sobre la configuración global.

## CLAW.md

No es JSON — un archivo markdown que el agente lee para el contexto del proyecto al inicio de cada sesión. Ver [Extender Panacea](extend.md) para lo que debe incluirse.

## Próximos pasos

- [Modos de permiso](../use-panacea/permission-modes.md)
- [Gestionar sesiones](../use-panacea/sessions.md)
