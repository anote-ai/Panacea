# Architektur

## Monorepo-Struktur

```
Panacea/
├── packages/
│   ├── backend/    # Python Flask — einheitliche API + Agenten-Streaming + RAG
│   ├── cli/        # TypeScript — anote Terminal-CLI
│   ├── vscode/     # TypeScript — VS Code-Erweiterung
│   ├── web/        # TypeScript/React — Browser-Chatbot-App
│   ├── mobile/     # TypeScript/React Native (Expo) — iOS + Android
│   ├── desktop/    # TypeScript/Electron — private Desktop-App
│   ├── sdk/        # TypeScript — JS/TS-Client-SDK
│   └── docs/       # MkDocs Material — Dokumentationsseite
├── docker-compose.yml
├── package.json    # npm-Arbeitsbereiche
└── Makefile
```

## Backend-Architektur

Das Python Flask-Backend verarbeitet die gesamte serverseitige Logik:

```
packages/backend/
├── app.py                    # Flask-Einstiegspunkt, Routenregistrierung
├── api_endpoints/
│   ├── chat/                 # Agenten-Streaming (SSE), Sitzungsverwaltung
│   ├── documents/            # Upload, RAG-Pipeline, Q&A
│   ├── search/               # Abfragen des semantischen Suchindex
│   ├── auth/                 # JWT, Google OAuth
│   ├── user/                 # Profil, Einstellungen
│   └── payments/             # Stripe-Webhooks + Checkout
├── agents/                   # LangChain/LangGraph-Agenten-Definitionen
├── services/
│   ├── rag.py                # Dokumentenchunking + Chroma-Embeddings
│   ├── streaming.py          # SSE-Streaming zu Claude/OpenAI/Gemini
│   └── search.py             # TF-IDF semantische Suche
├── database/
│   ├── db.py                 # MySQL-Verbindung + Abfragen
│   └── schema.sql            # Datenbankschema
└── models/                   # LLM-Anbieter-Wrappers
```

## Datenfluss: Agent-Chat

```
Client (CLI / VS Code / Web / Mobile)
    │  POST /api/chat/stream {message, cwd, model}
    ▼
Flask-Backend (app.py → chat/handler.py)
    │  SSE-Stream
    ▼
LLM-Anbieter (Anthropic / OpenAI / Gemini / Ollama)
    │  Toolaufrufe ↔ ausführen (Lesen/Schreiben/Bearbeiten/Bash/Glob/Grep)
    ▼
Dateisystem (cwd) + Chroma (RAG-Kontext)
```

## Technologieauswahl

| Schicht | Technologie | Warum |
|---|---|---|
| Backend | Python Flask | Reichhaltiges ML/AI-Ökosystem, bestehende Agenten |
| Agenten-Streaming | Anthropic Python SDK | Native SSE, Toolnutzung |
| Vektor-DB | ChromaDB | Local-first, keine Infrastruktur erforderlich |
| Datenbank | MySQL | ACID, bestehendes Schema |
| Cache | Redis | Sitzung + Ratenbegrenzung |
| Frontend | React 18 + TypeScript | Typensicherheit, Ökosystem |
| Desktop | Electron | Plattformübergreifend, bündelt Python |
| Mobile | Expo (React Native) | Code-Sharing mit Web |
| CLI | Commander.js | Ausgereift, TypeScript-freundlich |
| Docs | MkDocs Material | Schön, schnell, Markdown |
