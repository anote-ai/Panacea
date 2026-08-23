# API de Búsqueda

Ruta base: `/api/search`

## Índice de Código de Búsqueda

```http
GET /api/search?q=authentication&cwd=/path/to/project&top=10
Authorization: Bearer <token>
```

**Parámetros**

| Parámetro | Tipo    | Descripción                                         |
|-----------|---------|-----------------------------------------------------|
| `q`       | string  | Consulta de búsqueda (requerido)                   |
| `cwd`     | string  | Directorio del proyecto que contiene `.anote/index/` |
| `top`     | integer | Número de resultados a devolver (por defecto: 10)  |

**Respuesta**
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

Devuelve `404` si no existe un índice en el `cwd` dado. Primero construya un índice con `anote index`.
