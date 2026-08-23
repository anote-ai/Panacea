# Architecture

## Structure du Monorepo

```
Panacea/
├── packages/
│   ├── backend/    # Python Flask — API unifiée + streaming d'agent + RAG
│   ├── cli/        # TypeScript — terminal CLI anote
│   ├── vscode/     # TypeScript — extension VS Code
│   ├── web/        # TypeScript/React — application chatbot navigateur
│   ├── mobile/     # TypeScript/React Native (Expo) — iOS + Android
│   ├── desktop/    # TypeScript/Electron — application de bureau privée
│   ├── sdk/        # TypeScript — SDK client JS/TS
│   └── docs/       # MkDocs Material — site de documentation
├── docker-compose.yml
├── package.json    # espaces de travail npm
└── Makefile
```

## Architecture Backend

Le backend Python Flask gère toute la logique côté serveur :

```
packages/backend/
├── app.py                    # Point d'entrée Flask, enregistrement des routes
├── api_endpoints/
│   ├── chat/                 # Streaming d'agent (SSE), gestion de session
│   ├── documents/            # Téléchargement, pipeline RAG, Q&R
│   ├── search/               # Requêtes d'index de recherche sémantique
│   ├── auth/                 # JWT, Google OAuth
│   ├── user/                 # Profil, paramètres
│   └── payments/             # Webhooks Stripe + paiement
├── agents/                   # Définitions d'agents LangChain/LangGraph
├── services/
│   ├── rag.py                # Découpage de documents + embeddings Chroma
│   ├── streaming.py          # Streaming SSE vers Claude/OpenAI/Gemini
│   └── search.py             # Recherche sémantique TF-IDF
├── database/
│   ├── db.py                 # Connexion MySQL + requêtes
│   └── schema.sql            # Schéma de base de données
└── models/                   # Wrappers de fournisseurs LLM
```

## Flux de Données : Chat d'Agent

```
Client (CLI / VS Code / Web / Mobile)
    │  POST /api/chat/stream {message, cwd, model}
    ▼
Backend Flask (app.py → chat/handler.py)
    │  flux SSE
    ▼
Fournisseur LLM (Anthropic / OpenAI / Gemini / Ollama)
    │  appels d'outils ↔ exécuter (Lire/Écrire/Modifier/Bash/Glob/Grep)
    ▼
Système de fichiers (cwd) + Chroma (contexte RAG)
```

## Choix Technologiques

| Couche | Technologie | Pourquoi |
|---|---|---|
| Backend | Python Flask | Écosystème ML/AI riche, agents existants |
| Streaming d'agent | SDK Python Anthropic | SSE natif, utilisation d'outils |
| Base de données vectorielle | ChromaDB | Local-first, aucune infrastructure nécessaire |
| Base de données | MySQL | ACID, schéma existant |
| Cache | Redis | Session + limitation de débit |
| Frontend | React 18 + TypeScript | Sécurité de type, écosystème |
| Bureau | Electron | Multiplateforme, regroupe Python |
| Mobile | Expo (React Native) | Partage de code avec le web |
| CLI | Commander.js | Mûr, compatible TypeScript |
| Docs | MkDocs Material | Beau, rapide, markdown |
