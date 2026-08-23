# Such-API

Basis-Pfad: `/api/search`

## Such-Codebasis-Index

```http
GET /api/search?q=authentication&cwd=/path/to/project&top=10
Authorization: Bearer <token>
```

**Parameter**

| Parameter | Typ    | Beschreibung                              |
|-----------|--------|------------------------------------------|
| `q`       | string | Suchanfrage (erforderlich)               |
| `cwd`     | string | Projektverzeichnis, das `.anote/index/` enthält |
| `top`     | integer| Anzahl der zurückzugebenden Ergebnisse (Standard: 10) |

**Antwort**
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

Gibt `404` zurück, wenn kein Index im angegebenen `cwd` existiert. Erstellen Sie zuerst einen Index mit `anote index`.
