# API di Ricerca

Percorso base: `/api/search`

## Indicizzazione del Codice Sorgente

```http
GET /api/search?q=authentication&cwd=/path/to/project&top=10
Authorization: Bearer <token>
```

**Parametri**

| Parametro | Tipo | Descrizione |
|-----------|------|-------------|
| `q` | stringa | Query di ricerca (obbligatoria) |
| `cwd` | stringa | Directory del progetto contenente `.anote/index/` |
| `top` | intero | Numero di risultati da restituire (predefinito: 10) |

**Risposta**
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

Restituisce `404` se non esiste alcun indice nella `cwd` fornita. Crea prima un indice con `anote index`.
