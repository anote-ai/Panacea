# CLI Команды

## `anote ask`

Задайте любой вопрос о вашем коде.

```bash
anote ask "как работает промежуточное ПО аутентификации?"
anote ask --file src/auth.ts "объясните этот файл"
anote ask --compare  # сравнение бок о бок по нескольким моделям
cat file.py | anote ask "найти ошибки"
```

## `anote fix`

Исправьте ошибки в текущем каталоге.

```bash
anote fix
anote fix --loop                    # итерация до тех пор, пока тесты не пройдут
anote fix --max-iterations 5        # ограничить количество итераций
anote fix --file src/broken.ts      # исправить конкретный файл
```

## `anote review`

Проверьте код на наличие ошибок, проблем с безопасностью и качества.

```bash
anote review                        # проверить текущий каталог
anote review --file src/handler.ts  # проверить конкретный файл
anote review --pr 42                # опубликовать AI обзор на GitHub PR
```

## `anote index`

Создайте индекс семантического поиска TF-IDF вашего кода.

```bash
anote index              # индексировать текущий каталог
anote index --watch      # следить за изменениями и переиндексировать
anote index /path/to/dir # индексировать конкретный каталог
```

## `anote search`

Ищите семантически в вашем индексированном коде.

```bash
anote search "JWT токен валидации"
anote search "подключение к базе данных" --top 10
anote search "auth middleware" --json
```

## `anote doctor`

Проверьте вашу среду на наличие проблем с конфигурацией.

```bash
anote doctor
```

Проверки: Node.js ≥ 18, `ANTHROPIC_API_KEY` установлен, `.anote.json` присутствует, `CLAW.md` присутствует, git установлен.

## `anote changelog`

Сгенерируйте запись CHANGELOG.md из истории git.

```bash
anote changelog
anote changelog --since v1.2.0
anote changelog --dry-run
```

## `anote docs`

Сгенерируйте документацию для недокументированного кода.

```bash
anote docs
anote docs src/api.ts
anote docs --style jsdoc
anote docs --dry-run
```

## `anote migrate`

Миграция кода с помощью AI.

```bash
anote migrate --from "React 17" --to "React 18"
anote migrate --from "axios" --to "fetch"
anote migrate --dry-run
```

## `anote security`

Аудит безопасности вашего кода (OWASP Top 10).

```bash
anote security
anote security --severity high
anote security --fix
```

## `anote perf`

Анализ производительности.

```bash
anote perf
anote perf --focus "database,bundle"
anote perf --fix
```
