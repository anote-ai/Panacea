# API de Busca

Caminho base: `/api/search`

## Índice de Código da Busca

```http
GET /api/search?q=authentication&cwd=/path/to/project&top=10
Authorization: Bearer <token>
```

**Parâmetros**

| Parâmetro | Tipo   | Descrição                                      |
|-----------|--------|------------------------------------------------|
| `q`       | string | Consulta de busca (obrigatório)                |
| `cwd`     | string | Diretório do projeto contendo `.anote/index/` |
| `top`     | integer| Número de resultados a retornar (padrão: 10)   |

**Resposta**
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

Retorna `404` se nenhum índice existir no `cwd` fornecido. Construa um índice primeiro com `anote index`.
