# Поиск API

Базовый путь: `/api/search`

## Индекс кода поиска

```http
GET /api/search?q=authentication&cwd=/path/to/project&top=10
Authorization: Bearer <token>
```

**Параметры**

| Параметр | Тип    | Описание                                      |
|----------|--------|-----------------------------------------------|
| `q`      | строка | Поисковый запрос (обязательный)              |
| `cwd`    | строка | Директория проекта, содержащая `.anote/index/` |
| `top`    | целое  | Количество результатов для возврата (по умолчанию: 10) |

**Ответ**
```json
{
  "results": [
    {
      "file": "src/auth/handler.py",
      "startLine": 45,
      "endLine": 72,
      "preview": "def authenticate_user(email, password)...",
      "score": 0.8432
    }
  ]
}
```

Возвращает `404`, если индекс не существует в указанном `cwd`. Сначала создайте индекс с помощью `anote index`.
