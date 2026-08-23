# Configuración de la Extensión de VS Code

Configura la extensión en la interfaz de configuración de VS Code o en `settings.json`.

| Configuración | Predeterminado | Descripción |
|---------------|----------------|-------------|
| `anote.model` | `claude-sonnet-4-6` | Modelo predeterminado a utilizar |
| `anote.apiKey` | `""` | Clave API de Anthropic (o usar variable de entorno) |
| `anote.permissionMode` | `default` | Modo de permiso de la herramienta: `default`, `auto`, `manual` |
| `anote.showToolUse` | `true` | Mostrar llamadas a la herramienta en el panel de chat |

```json
{
  "anote.model": "claude-sonnet-4-6",
  "anote.permissionMode": "default"
}
```
