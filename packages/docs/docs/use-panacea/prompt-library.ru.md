# Библиотека запросов

Копируйте и вставляйте запросы для `anote ask`, `anote chat` и `anote fix`, организованные по задачам.

## Понимание кода

```bash
anote ask "что делает эта кодовая база на высоком уровне?"
anote ask --file src/payments/webhook.ts "пройди со мной по этому файлу строка за строкой"
anote ask "где настроен ограничитель скорости и каковы его лимиты?"
anote ask "что сломается, если я уберу уровень кэширования здесь?"
```

## Отладка

```bash
anote fix --error "$(cat error.log)"
anote ask "почему этот тест иногда не проходит, но не постоянно?"
anote fix src/db/pool.ts "соединения не возвращаются обратно в пул"
```

## Код-ревью

```bash
anote review --file src/auth/session.ts
anote review --pr 42
anote diff --staged -c "сосредоточьтесь на обработке ошибок и крайних случаях"
```

## Рефакторинг

```bash
anote refactor src/utils.ts "разделите это на более мелкие функции с одной целью" --dry-run
anote ask "есть ли более простой способ выразить эту логику?" --file src/parser.ts
anote migrate --from "moment" --to "date-fns"
```

## Написание тестов

```bash
anote test src/utils/validate.ts --coverage --write
anote ask "какие крайние случаи я упускаю для этой функции?" --file src/utils/validate.ts
```

## Безопасность и производительность

```bash
anote security --severity high
anote perf --focus "база данных, размер пакета"
```

## Документация

```bash
anote docs src/api/client.ts --style jsdoc
anote changelog --since v1.2.0
anote explain --stdout                       # краткое резюме архитектуры
```

## Следующие шаги

- [Общие рабочие процессы](common-workflows.md)
- [Команды CLI](../cli/commands.md)
