# Изучите каталог .anote

CLI Panacea считывает конфигурацию из двух мест: файла для каждого проекта и глобального.

## Конфигурация проекта

Panacea ищет вверх от вашей текущей директории первый найденный файл в следующем порядке:

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

| Ключ | Назначение |
|---|---|
| `model` | Модель по умолчанию для этого проекта |
| `permissionMode` | `default`, `acceptEdits` или `bypassPermissions` — см. [Режимы разрешений](../use-panacea/permission-modes.md) |
| `provider` | Явное переопределение провайдера (обычно автоматически определяется из `model`) |
| `baseUrl` | Базовый URL для совместимых с OpenAI конечных точек, например, `http://localhost:11434/v1` для Ollama |
| `maxTurns` | Лимит ходов на сеанс |
| `compactAfterMessages` | Когда сжимать историю сеанса |
| `hooks` | `preToolUse` / `postToolUse` хуки оболочки — см. [Расширьте Panacea](extend.md) |

`anote init` создает `.anote.json` для вас. `anote config` считывает и записывает его:

```bash
anote config              # показать эффективную конфигурацию (глобальную + локальную)
anote config get model
anote config set model gpt-4.1
anote config path         # напечатать путь к глобальному конфигурационному файлу
anote config edit         # открыть глобальную конфигурацию в $EDITOR
```

## Глобальная конфигурация

`~/.anote/config.json` содержит ваши настройки по умолчанию — применяются, когда проект их не переопределяет. Конфигурация проекта всегда имеет приоритет над глобальной конфигурацией.

## CLAW.md

Не JSON — файл markdown, который агент считывает для контекста проекта в начале каждой сессии. См. [Расширьте Panacea](extend.md) для того, что должно быть в нем.

## Следующие шаги

- [Режимы разрешений](../use-panacea/permission-modes.md)
- [Управление сессиями](../use-panacea/sessions.md)
