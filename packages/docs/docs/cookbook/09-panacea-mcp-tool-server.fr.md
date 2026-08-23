# Serveur d'outils MCP de Panacea

Cette recette explique comment Panacea expose ses primitives de document/chat en tant qu'outils standard [Model Context Protocol](https://modelcontextprotocol.io/) (MCP), afin que tout client compatible MCP (Claude Desktop, autres hôtes MCP) puisse utiliser directement les capacités de récupération et d'historique de chat de Panacea.

## Ce que vous allez apprendre

- La différence entre cette surface MCP et l'architecture d'enregistrement d'agent/outils interne de la recette 04
- Quelles opérations de document et de chat sont exposées en tant qu'outils MCP
- Comment l'ingestion de documents reste non-bloquante via une tâche distante Ray
- Pourquoi l'outil de passage SQL brut est une considération de sécurité qui mérite d'être soulignée

## Pourquoi cela importe

La recette 04 couvre comment l'orchestrateur *interne* de Panacea enregistre des outils pour que ses propres agents les appellent. Il s'agit d'une surface d'intégration différente : elle regroupe les mêmes fonctions de document/chat sous-jacentes en tant qu'**outils MCP externes et standardisés** que tout client MCP peut invoquer — aucun SDK ou contrat API spécifique à Panacea n'est requis, juste le protocole MCP.

## Fichiers clés de Panacea

| Fichier | Pourquoi cela importe |
|---|---|
| `Panacea/backend/mcp/mcp_server.py` | `FastMCP("Document Agent Server")` — définit tous les neuf outils MCP |
| `Panacea/backend/api_endpoints/financeGPT/chatbot_endpoints.py` | Les fonctions sous-jacentes orientées base de données que chaque outil MCP encapsule (`get_relevant_chunks`, `add_document_to_db`, `chunk_document`, etc.) |
| `Panacea/backend/database/db.py` | `get_db_connection` — utilisé directement par l'outil `execute_database_query` |

## Comment cela fonctionne

1. `mcp_server.py` initialise Ray (`ray.init(...)`) et une instance de serveur `FastMCP` nommée `"Document Agent Server"`.
2. Chaque fonction décorée avec `@mcp.tool()` encapsule une fonction existante de Panacea et retourne un résultat en texte brut ou une chaîne d'erreur — la forme qu'un appel d'outil LLM attend en retour :
   - `retrieve_relevant_chunks(query, chat_id, user_email, k=2)` — recherche sémantique sur les documents d'un chat via `get_relevant_chunks`
   - `ingest_document(text, document_name, chat_id, chunk_size=1000)` — enregistre un document via `add_document_to_db`
   - `list_documents(chat_id, user_email)` / `delete_document(doc_id, user_email)` — gestion de documents
   - `add_message` / `get_chat_history` — lecture/écriture de l'historique de chat
   - `add_sources_to_message` — attacher des citations à un message stocké
   - `extract_text_from_url(url)` — récupérer et retourner le contenu texte d'une URL
   - `execute_database_query(query, params)` — passage SQL brut (voir note de sécurité ci-dessous)
3. `ingest_document` ne bloque pas sur le fractionnement — il appelle `chunk_document.remote(text, chunk_size, doc_id)`, une tâche distante Ray, donc les grands documents sont traités de manière asynchrone tandis que l'appel d'outil retourne immédiatement.
4. Exécuter `python backend/mcp/mcp_server.py` démarre `mcp.run()`, qui sert ces outils via le transport stdio de MCP — prêt pour qu'un client MCP se lance et se connecte.
5. Un client MCP (par exemple, Claude Desktop) configuré pour lancer ce script a accès à tous les neuf outils automatiquement, sans écrire de code d'intégration spécifique à Panacea.

### Note de sécurité

`execute_database_query` exécute une chaîne SQL arbitraire contre la connexion de production sans liste d'autorisation ni restriction en lecture seule — les requêtes `SELECT` retournent des lignes au format JSON, tout autre chose s'engage et retourne le nombre de lignes affectées. Considérez cela comme un territoire de moindre privilège : si vous exposez ce serveur à un client MCP que vous ne faites pas entièrement confiance, soit retirez cet outil, soit limitez son utilisateur de base de données à un accès en lecture seule sur des tables non sensibles.

## Exécutez-le localement

Depuis la racine de l'espace de travail (`anote/panacea`):

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build   # démarre MySQL, Redis, Tika et le backend
```

Le serveur MCP a besoin de `fastmcp` (actuellement non spécifié dans `backend/requirements.txt` — installez-le séparément) et de `ray>=2.9.0` (déjà dans `backend/requirements.txt`) :

```bash
pip install fastmcp
cd Panacea/backend
python mcp/mcp_server.py
```

### Connecter un client MCP

Pointez un client compatible MCP vers le script, par exemple dans `claude_desktop_config.json` de Claude Desktop :

```json
{
  "mcpServers": {
    "panacea-documents": {
      "command": "python",
      "args": ["/absolute/path/to/Panacea/backend/mcp/mcp_server.py"]
    }
  }
}
```

Redémarrez le client, et les neuf outils ci-dessus deviennent disponibles pour être invoqués depuis le chat.

## Remarques pour le livre de recettes

Bon suivi de la recette 04 — contrastez l'enregistrement d'outils internes (`register_tool()` à l'intérieur de l'orchestrateur) avec cette surface MCP externe. Il convient également de noter comme un écart pour les lecteurs : `fastmcp` n'est pas encore listé dans `backend/requirements.txt`, donc il nécessite une installation manuelle jusqu'à ce que cela soit corrigé en amont.
