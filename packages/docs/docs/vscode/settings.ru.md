# Настройки расширения VS Code

Настройте расширение в пользовательском интерфейсе настроек VS Code или в `settings.json`.

| Настройка | По умолчанию | Описание |
|-----------|--------------|----------|
| `anote.model` | `claude-sonnet-4-6` | Модель по умолчанию для использования |
| `anote.apiKey` | `""` | Ключ API Anthropic (или используйте переменную окружения) |
| `anote.permissionMode` | `default` | Режим разрешений инструмента: `default`, `auto`, `manual` |
| `anote.showToolUse` | `true` | Показывать вызовы инструментов в панели чата |

```json
{
  "anote.model": "claude-sonnet-4-6",
  "anote.permissionMode": "default"
}
```
