# Общие рабочие процессы

Пошаговые шаблоны для повседневных задач с помощью CLI Panacea.

## Изучение незнакомой кодовой базы

```bash
anote explain                       # создать обзор CODEBASE.md
anote explain src/auth.ts "как это работает?"
anote index && anote search "JWT validation"
```

`explain` без аргументов создает обзор `CODEBASE.md` всей репозитории. Укажите файл или задайте конкретный вопрос для более глубокого изучения.

## Исправление ошибки

```bash
anote fix --error "TypeError: cannot read property 'id' of undefined"
anote fix src/handler.ts "обработчик вебхуков теряет события под нагрузкой"
anote fix --loop --cmd "npm test"          # продолжать итерации, пока тесты не пройдут
```

## Написание и коммит

```bash
anote generate "middleware для ограничения скорости для Express" -o src/middleware/rateLimit.ts
anote test src/middleware/rateLimit.ts --write
anote commit                                # сообщение коммита, сгенерированное ИИ
```

## Проверка перед отправкой

```bash
anote diff --staged                         # просмотреть подготовленные изменения
anote review --pr 42                        # или просмотреть открытый PR на GitHub
anote security --severity high              # аудит OWASP Top 10
```

## Открытие запроса на слияние

```bash
anote pr --gh                               # сгенерировать описание, открыть с помощью gh CLI
```

## Безопасный рефакторинг

```bash
anote refactor src/legacy.ts "извлечь логику валидации в отдельную функцию" --dry-run
anote refactor src/legacy.ts "извлечь логику валидации в отдельную функцию" --auto
```

Всегда сначала пробуйте `--dry-run` на чем-то, что вы еще не проверяли.

## Продолжайте работать, пока делаете что-то другое

```bash
anote watch "src/**/*.ts"                   # повторно анализировать при каждом сохранении
```

## Документируйте по мере работы

```bash
anote docs src/api.ts --style jsdoc
anote changelog --since v1.2.0
```

## Следующие шаги

- [Библиотека подсказок](prompt-library.md) — начальные точки для копирования и вставки
- [CLI команды](../cli/commands.md) — полный справочник по флагам
