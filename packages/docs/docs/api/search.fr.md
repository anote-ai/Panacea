# API de Recherche

Chemin de base : `/api/search`

## Index de Code de Recherche

```http
GET /api/search?q=authentication&cwd=/path/to/project&top=10
Authorization: Bearer <token>
```

**Paramètres**

| Paramètre | Type   | Description                                         |
|-----------|--------|-----------------------------------------------------|
| `q`       | string | Requête de recherche (obligatoire)                  |
| `cwd`     | string | Répertoire du projet contenant `.anote/index/`     |
| `top`     | integer| Nombre de résultats à retourner (par défaut : 10)   |

**Réponse**
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

Renvoie `404` si aucun index n'existe au `cwd` donné. Construisez d'abord un index avec `anote index`.
