# Configuración de CLI

El CLI de Anote se puede configurar a través de `.anote.json` en la raíz de tu proyecto o `~/.anote/config.json` globalmente.

## Archivo de Configuración

```json
{
  "model": "claude-sonnet-4-6",
  "permissionMode": "default",
  "maxTurns": 20,
  "provider": "anthropic"
}
```

## Gestión de Configuración

```bash
anote config list          # Mostrar todas las configuraciones
anote config get model     # Obtener un valor
anote config set model claude-haiku-4-5-20251001  # Establecer un valor
anote config unset model   # Eliminar un valor
```
