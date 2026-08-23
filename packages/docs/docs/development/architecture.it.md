# Architettura

## Struttura del Monorepo

```
Panacea/
├── packages/
│   ├── backend/    # Python Flask — API unificata + streaming agent + RAG
│   ├── cli/        # TypeScript — terminale CLI di anote
│   ├── vscode/     # TypeScript — estensione per VS Code
│   ├── web/        # TypeScript/React — app chatbot per browser
│   ├── mobile/     # TypeScript/React Native (Expo) — iOS + Android
│   ├── desktop/    # TypeScript/Electron — app desktop privata
│   ├── sdk/        # TypeScript — SDK client JS/TS
│   └── docs/       # MkDocs Material — sito di documentazione
├── docker-compose.yml
├── package.json    # spazi di lavoro npm
└── Makefile
```

## Architettura del Backend

Il backend Python Flask gestisce tutta la logica lato server:

```
packages/backend/
├── app.py                    # Punto di ingresso Flask, registrazione delle route
├── api_endpoints/
│   ├── chat/                 # Streaming agent (SSE), gestione delle sessioni
│   ├── documents/            # Caricamento, pipeline RAG, Q&A
│   ├── search/               # Query dell'indice di ricerca semantica
│   ├── auth/                 # JWT, Google OAuth
│   ├── user/                 # Profilo, impostazioni
│   └── payments/             # Webhook Stripe + checkout
├── agents/                   # Definizioni degli agenti LangChain/LangGraph
├── services/
│   ├── rag.py                # Suddivisione dei documenti + embeddings Chroma
│   ├── streaming.py          # Streaming SSE a Claude/OpenAI/Gemini
│   └── search.py             # Ricerca semantica TF-IDF
├── database/
│   ├── db.py                 # Connessione MySQL + query
│   └── schema.sql            # Schema del database
└── models/                   # Wrapper per fornitori di LLM
```

## Flusso di Dati: Chat dell'Agente

```
Client (CLI / VS Code / Web / Mobile)
    │  POST /api/chat/stream {message, cwd, model}
    ▼
Backend Flask (app.py → chat/handler.py)
    │  Stream SSE
    ▼
Fornitore LLM (Anthropic / OpenAI / Gemini / Ollama)
    │  chiamate agli strumenti ↔ esegui (Leggi/Scrivi/Modifica/Bash/Glob/Grep)
    ▼
Filesystem (cwd) + Chroma (contesto RAG)
```

## Scelte Tecnologiche

| Livello | Tecnologia | Perché |
|---|---|---|
| Backend | Python Flask | Ecosistema ML/AI ricco, agenti esistenti |
| Streaming agent | Anthropic Python SDK | SSE nativo, utilizzo degli strumenti |
| DB vettoriale | ChromaDB | Locale prima, nessuna infrastruttura necessaria |
| Database | MySQL | ACID, schema esistente |
| Cache | Redis | Sessione + limitazione della velocità |
| Frontend | React 18 + TypeScript | Sicurezza dei tipi, ecosistema |
| Desktop | Electron | Multipiattaforma, include Python |
| Mobile | Expo (React Native) | Condivisione del codice con il web |
| CLI | Commander.js | Maturo, compatibile con TypeScript |
| Docs | MkDocs Material | Bello, veloce, markdown |
