# Управление сессиями

Каждый разговор `anote chat` сохраняется локально как сессия — ее сообщения, использование токенов и рабочий каталог.

## Список сессий

```bash
anote sessions list
anote sessions ls --limit 50
```

```
Сохраненные сессии (3):
  a1b2c3d4  12 сообщений  in=4,200 out=1,800  10м назад  /Users/you/project
  e5f6a7b8  4 сообщения   in=900 out=400      2ч назад   /Users/you/other-project
```

## Показать сессию

```bash
anote sessions show a1b2c3d4
anote sessions show a1b2c3d4 --limit 50   # больше истории сообщений
```

Выводит разговор, общие токены и рабочий каталог для этой сессии. Вы можете передать короткий префикс ID сессии вместо полного.

## Удалить сессию

```bash
anote sessions delete a1b2c3d4
anote sessions rm a1b2c3d4
```

## Следующие шаги

- [Общие рабочие процессы](common-workflows.md)
- [Как работает Panacea](../core-concepts/how-it-works.md) — повороты, сжатие и как длина сессии влияет на контекст
