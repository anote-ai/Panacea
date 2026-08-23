# Журнал изменений

Panacea еще не публикует вручную поддерживаемый файл журнала изменений — источником правды о том, что было выпущено, является:

- **[Релизы на GitHub](https://github.com/anote-ai/Panacea/releases)** — помеченные релизы для CLI, расширения VS Code и других пакетов
- **[История коммитов](https://github.com/anote-ai/Panacea/commits/main)** — каждое изменение, в порядке

## Сгенерируйте один для вашего проекта

CLI может создать журнал изменений из истории git для *вашего* кода:

```bash
anote changelog                    # с последнего тега
anote changelog --since v1.2.0
anote changelog --dry-run          # вывести вместо записи в CHANGELOG.md
```

Это записывает в собственный `CHANGELOG.md` вашего проекта, а не Panacea.
