# Panacea MCP Tool Server

Questa ricetta spiega come Panacea espone le sue primitive di documento/chat come strumenti standard [Model Context Protocol](https://modelcontextprotocol.io/) (MCP), in modo che qualsiasi client compatibile con MCP (Claude Desktop, altri host MCP) possa utilizzare direttamente le capacità di recupero e cronologia chat di Panacea.

## Cosa imparerai

- La differenza tra questa superficie MCP e l'architettura interna di registrazione agenti/strumenti della ricetta 04
- Quali operazioni su documenti e chat sono esposte come strumenti MCP
- Come l'ingestione dei documenti rimane non bloccante tramite un'attività remota Ray
- Perché lo strumento di passaggio SQL grezzo è una considerazione di sicurezza degna di nota

## Perché è importante

La ricetta 04 tratta di come l'*orchestratore interno* di Panacea registra strumenti per i propri agenti da chiamare. Questa è una superficie di integrazione diversa: impacchetta le stesse funzioni sottostanti di documento/chat come **strumenti MCP esterni e standardizzati** che qualsiasi client MCP può invocare — non è richiesto alcun contratto SDK o API specifico di Panacea, solo il protocollo MCP.

## File chiave di Panacea

| File | Perché è importante |
|---|---|
| `Panacea/backend/mcp/mcp_server.py` | `FastMCP("Document Agent Server")` — definisce tutti e nove gli strumenti MCP |
| `Panacea/backend/api_endpoints/financeGPT/chatbot_endpoints.py` | Le funzioni sottostanti che ogni strumento MCP avvolge (`get_relevant_chunks`, `add_document_to_db`, `chunk_document`, ecc.) |
| `Panacea/backend/database/db.py` | `get_db_connection` — utilizzato direttamente dallo strumento `execute_database_query` |

## Come funziona

1. `mcp_server.py` inizializza Ray (`ray.init(...)`) e un'istanza del server `FastMCP` chiamata `"Document Agent Server"`.
2. Ogni funzione decorata con `@mcp.tool()` avvolge una funzione esistente di Panacea e restituisce un risultato in testo semplice o una stringa di errore — la forma che una chiamata a uno strumento LLM si aspetta indietro:
   - `retrieve_relevant_chunks(query, chat_id, user_email, k=2)` — ricerca semantica sui documenti di una chat tramite `get_relevant_chunks`
   - `ingest_document(text, document_name, chat_id, chunk_size=1000)` — registra un documento tramite `add_document_to_db`
   - `list_documents(chat_id, user_email)` / `delete_document(doc_id, user_email)` — gestione dei documenti
   - `add_message` / `get_chat_history` — lettura/scrittura della cronologia chat
   - `add_sources_to_message` — allega citazioni a un messaggio memorizzato
   - `extract_text_from_url(url)` — recupera e restituisce il contenuto testuale da un URL
   - `execute_database_query(query, params)` — passaggio SQL grezzo (vedi nota di sicurezza qui sotto)
3. `ingest_document` non blocca durante il chunking — chiama `chunk_document.remote(text, chunk_size, doc_id)`, un'attività remota Ray, quindi i documenti di grandi dimensioni vengono elaborati in modo asincrono mentre la chiamata allo strumento restituisce immediatamente.
4. Eseguendo `python backend/mcp/mcp_server.py` si avvia `mcp.run()`, che serve questi strumenti tramite il trasporto stdio di MCP — pronto per un client MCP da avviare e connettersi.
5. Un client MCP (ad es. Claude Desktop) configurato per avviare questo script ottiene accesso a tutti e nove gli strumenti automaticamente, senza scrivere alcun codice di integrazione specifico di Panacea.

### Nota di sicurezza

`execute_database_query` esegue una stringa SQL arbitraria contro la connessione di produzione senza alcuna lista di autorizzazione o restrizione di sola lettura — le query `SELECT` restituiscono righe come JSON, qualsiasi altra cosa impegna e restituisce il conteggio delle righe interessate. Tratta questo come territorio di minimo privilegio: se esponi questo server a un client MCP di cui non ti fidi completamente, rimuovi questo strumento o limita il suo utente DB a accesso in sola lettura su tabelle non sensibili.

## Eseguilo localmente

Dalla radice del workspace (`anote/panacea`):

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build   # avvia MySQL, Redis, Tika e il backend
```

Il server MCP ha bisogno di `fastmcp` (non attualmente specificato in `backend/requirements.txt` — installalo separatamente) e `ray>=2.9.0` (già presente in `backend/requirements.txt`):

```bash
pip install fastmcp
cd Panacea/backend
python mcp/mcp_server.py
```

### Collega un client MCP

Punta un client compatibile con MCP allo script, ad esempio nel `claude_desktop_config.json` di Claude Desktop:

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

Riavvia il client e i nove strumenti sopra diventano disponibili per essere invocati dalla chat.

## Note per il ricettario

Buon seguito alla ricetta 04 — confronta la registrazione interna degli strumenti (`register_tool()` all'interno dell'orchestratore) con questa superficie MCP esterna. Vale anche la pena notare come una lacuna per i lettori: `fastmcp` non è ancora elencato in `backend/requirements.txt`, quindi necessita di un'installazione manuale fino a quando non sarà corretto upstream.
