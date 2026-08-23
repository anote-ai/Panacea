# Конфигурация CLI

Anote CLI можно настроить через `.anote.json` в корне вашего проекта или `~/.anote/config.json` глобально.

## Файл конфигурации

```json
{
  "model": "claude-sonnet-4-6",
  "permissionMode": "default",
  "maxTurns": 20,
  "provider": "anthropic"
}
```

## Управление конфигурацией

```bash
anote config list          # Показать все настройки
anote config get model     # Получить значение
anote config set model claude-haiku-4-5-20251001  # Установить значение
anote config unset model   # Удалить значение
```
