# Panacea MCP Tool Server

Dieses Rezept erklärt, wie Panacea seine Dokument-/Chat-Primitiven als standardisierte [Model Context Protocol](https://modelcontextprotocol.io/) (MCP) Werkzeuge bereitstellt, sodass jeder MCP-kompatible Client (Claude Desktop, andere MCP-Hosts) die Abruf- und Chatverlauf-Funktionen von Panacea direkt nutzen kann.

## Was Sie lernen werden

- Der Unterschied zwischen dieser MCP-Oberfläche und der internen Agenten-/Werkzeugregistrierungsarchitektur aus Rezept 04
- Welche Dokument- und Chatoperationen als MCP-Werkzeuge bereitgestellt werden
- Wie die Dokumentenaufnahme nicht-blockierend über eine Ray-Remote-Aufgabe bleibt
- Warum das rohe SQL-Passthrough-Werkzeug eine Sicherheitsüberlegung ist, die es wert ist, hervorgehoben zu werden

## Warum das wichtig ist

Rezept 04 behandelt, wie Panaceas *interner* Orchestrator Werkzeuge für seine eigenen Agenten registriert. Dies ist eine andere Integrationsoberfläche: Sie verpackt die gleichen zugrunde liegenden Dokument-/Chat-Funktionen als **externe, standardisierte MCP-Werkzeuge**, die jeder MCP-Client aufrufen kann — kein Panacea-spezifisches SDK oder API-Vertrag erforderlich, nur das MCP-Protokoll.

## Wichtige Panacea-Dateien

| Datei | Warum es wichtig ist |
|---|---|
| `Panacea/backend/mcp/mcp_server.py` | `FastMCP("Document Agent Server")` — definiert alle neun MCP-Werkzeuge |
| `Panacea/backend/api_endpoints/financeGPT/chatbot_endpoints.py` | Die zugrunde liegenden DB-facing Funktionen, die jedes MCP-Werkzeug umschließt (`get_relevant_chunks`, `add_document_to_db`, `chunk_document` usw.) |
| `Panacea/backend/database/db.py` | `get_db_connection` — wird direkt vom `execute_database_query` Werkzeug verwendet |

## Wie es funktioniert

1. `mcp_server.py` initialisiert Ray (`ray.init(...)`) und eine `FastMCP` Serverinstanz mit dem Namen `"Document Agent Server"`.
2. Jede Funktion, die mit `@mcp.tool()` dekoriert ist, umschließt eine vorhandene Panacea-Funktion und gibt ein Ergebnis oder eine Fehlermeldung im Klartext zurück — die Form, die ein LLM-Werkzeugaufruf erwartet:
   - `retrieve_relevant_chunks(query, chat_id, user_email, k=2)` — semantische Suche über die Dokumente eines Chats via `get_relevant_chunks`
   - `ingest_document(text, document_name, chat_id, chunk_size=1000)` — registriert ein Dokument über `add_document_to_db`
   - `list_documents(chat_id, user_email)` / `delete_document(doc_id, user_email)` — Dokumentenverwaltung
   - `add_message` / `get_chat_history` — Lesen/Schreiben des Chatverlaufs
   - `add_sources_to_message` — Zitationen an einer gespeicherten Nachricht anhängen
   - `extract_text_from_url(url)` — Textinhalt von einer URL abrufen und zurückgeben
   - `execute_database_query(query, params)` — rohes SQL-Passthrough (siehe Sicherheitsnotiz unten)
3. `ingest_document` blockiert nicht beim Chunking — es ruft `chunk_document.remote(text, chunk_size, doc_id)` auf, eine Ray-Remote-Aufgabe, sodass große Dokumente asynchron verarbeitet werden, während der Werkzeugaufruf sofort zurückgegeben wird.
4. Das Ausführen von `python backend/mcp/mcp_server.py` startet `mcp.run()`, das diese Werkzeuge über MCPs stdio-Transport bereitstellt — bereit für einen MCP-Client, um zu starten und sich zu verbinden.
5. Ein MCP-Client (z. B. Claude Desktop), der so konfiguriert ist, dass er dieses Skript startet, erhält automatisch Zugriff auf alle neun Werkzeuge, ohne dass spezifischer Integrationscode für Panacea geschrieben werden muss.

### Sicherheitsnotiz

`execute_database_query` führt eine beliebige SQL-Zeichenfolge gegen die Produktionsverbindung aus, ohne eine Allow-List oder eine schreibgeschützte Einschränkung — `SELECT`-Abfragen geben Zeilen als JSON zurück, alles andere commit und gibt die Anzahl der betroffenen Zeilen zurück. Behandeln Sie dies als Bereich mit minimalen Berechtigungen: Wenn Sie diesen Server einem MCP-Client aussetzen, dem Sie nicht vollständig vertrauen, entfernen Sie entweder dieses Werkzeug oder beschränken Sie seinen DB-Benutzer auf schreibgeschützten Zugriff auf nicht-sensitive Tabellen.

## Lokal ausführen

Vom Arbeitsbereichs-Stammverzeichnis (`anote/panacea`):

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build   # startet MySQL, Redis, Tika und das Backend
```

Der MCP-Server benötigt `fastmcp` (derzeit nicht in `backend/requirements.txt` festgelegt — separat installieren) und `ray>=2.9.0` (bereits in `backend/requirements.txt`):

```bash
pip install fastmcp
cd Panacea/backend
python mcp/mcp_server.py
```

### Einen MCP-Client verbinden

Richten Sie einen MCP-kompatiblen Client auf das Skript aus, z. B. in Claudes `claude_desktop_config.json`:

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

Starten Sie den Client neu, und die neun oben genannten Werkzeuge stehen zur Verfügung, um sie aus dem Chat aufzurufen.

## Hinweise für das Kochbuch

Gute Fortsetzung zu Rezept 04 — kontrastieren Sie die interne Werkzeugregistrierung (`register_tool()` innerhalb des Orchestrators) mit dieser externen MCP-Oberfläche. Es ist auch erwähnenswert, dass `fastmcp` noch nicht in `backend/requirements.txt` aufgeführt ist, sodass es bis zur Behebung upstream manuell installiert werden muss.
