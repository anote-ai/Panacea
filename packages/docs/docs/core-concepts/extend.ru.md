# Расширение Panacea

Есть два способа настроить поведение Panacea в вашем проекте: **CLAW.md** для постоянных инструкций и **хуки** для запуска собственных команд вокруг вызовов инструментов.

## CLAW.md — память проекта

`CLAW.md` — это markdown-файл, который Panacea читает для получения контекста проекта — та же идея, что и README, только адресованная агенту, а не человеку. `anote init` автоматически генерирует его, предзаполняя обнаруженным стеком и командами проверки (test/lint/build):

```markdown
# CLAW.md

This file provides guidance to Anote AI when working with code in this repository.

## Project overview

<!-- Describe what this project does -->

## Stack

TypeScript · Next.js

## Verification

Run these before considering a change complete:

  npm test
  npm run lint

## Working agreement

- Read relevant files before making changes
- Run the verification commands after modifying logic
- Keep changes small and focused
- Prefer editing existing files over creating new ones
```

Редактируйте его свободно — добавляйте заметки об архитектуре, соглашения или моменты, в которых агент постоянно ошибается. Panacea читает его в начале каждой сессии в этой директории.

## Хуки — запуск собственных команд вокруг вызовов инструментов

Хуки запускают команду оболочки до (`preToolUse`) или после (`postToolUse`) каждого вызова инструмента, настраиваются в `.anote.json`:

```json
{
  "hooks": {
    "preToolUse": ["./scripts/check-tool-policy.sh"],
    "postToolUse": ["npx prettier --write ."]
  }
}
```

**Семантика кодов завершения:**

| Код завершения | Эффект |
|---|---|
| `0` | Разрешить — stdout захватывается как информационное сообщение |
| `2` | Запретить — stdout захватывается как причина и показывается агенту |
| любой другой | Предупредить, но разрешить |

Используйте `preToolUse`, чтобы блокировать рискованные команды или применять политику до их выполнения; используйте `postToolUse` для таких вещей, как автоформатирование после каждой правки.

## Дальнейшие шаги

- [Изучение директории .anote](anote-directory.md) — где находятся CLAW.md и конфигурация
- [Режимы разрешений](../use-panacea/permission-modes.md) — другой рычаг управления тем, что может делать агент
