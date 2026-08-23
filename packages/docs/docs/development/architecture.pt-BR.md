# Arquitetura

## Estrutura do Monorepo

```
Panacea/
├── pacotes/
│   ├── backend/    # Python Flask — API unificada + streaming de agente + RAG
│   ├── cli/        # TypeScript — terminal CLI anote
│   ├── vscode/     # TypeScript — extensão do VS Code
│   ├── web/        # TypeScript/React — aplicativo de chatbot para navegador
│   ├── mobile/     # TypeScript/React Native (Expo) — iOS + Android
│   ├── desktop/    # TypeScript/Electron — aplicativo de desktop privado
│   ├── sdk/        # TypeScript — SDK cliente JS/TS
│   └── docs/       # MkDocs Material — site de documentação
├── docker-compose.yml
├── package.json    # workspaces npm
└── Makefile
```

## Arquitetura do Backend

O backend em Python Flask lida com toda a lógica do lado do servidor:

```
pacotes/backend/
├── app.py                    # Ponto de entrada do Flask, registro de rotas
├── api_endpoints/
│   ├── chat/                 # Streaming de agente (SSE), gerenciamento de sessão
│   ├── documents/            # Upload, pipeline RAG, Q&A
│   ├── search/               # Consultas de índice de busca semântica
│   ├── auth/                 # JWT, Google OAuth
│   ├── user/                 # Perfil, configurações
│   └── payments/             # Webhooks do Stripe + checkout
├── agents/                   # Definições de agentes LangChain/LangGraph
├── services/
│   ├── rag.py                # Fragmentação de documentos + embeddings Chroma
│   ├── streaming.py          # Streaming SSE para Claude/OpenAI/Gemini
│   └── search.py             # Busca semântica TF-IDF
├── database/
│   ├── db.py                 # Conexão MySQL + consultas
│   └── schema.sql            # Esquema do banco de dados
└── models/                   # Wrappers de provedores de LLM
```

## Fluxo de Dados: Chat do Agente

```
Cliente (CLI / VS Code / Web / Mobile)
    │  POST /api/chat/stream {mensagem, cwd, modelo}
    ▼
Backend Flask (app.py → chat/handler.py)
    │  fluxo SSE
    ▼
Provedor de LLM (Anthropic / OpenAI / Gemini / Ollama)
    │  chamadas de ferramenta ↔ executar (Ler/Escrever/Editar/Bash/Glob/Grep)
    ▼
Sistema de Arquivos (cwd) + Chroma (contexto RAG)
```

## Escolhas Tecnológicas

| Camada | Tecnologia | Por quê |
|---|---|---|
| Backend | Python Flask | Ecossistema rico em ML/AI, agentes existentes |
| Streaming de agente | Anthropic Python SDK | SSE nativo, uso de ferramentas |
| Banco de Dados Vetorial | ChromaDB | Local-first, sem infraestrutura necessária |
| Banco de Dados | MySQL | ACID, esquema existente |
| Cache | Redis | Sessão + limitação de taxa |
| Frontend | React 18 + TypeScript | Segurança de tipo, ecossistema |
| Desktop | Electron | Multiplataforma, empacota Python |
| Mobile | Expo (React Native) | Compartilhamento de código com a web |
| CLI | Commander.js | Maduro, amigável ao TypeScript |
| Docs | MkDocs Material | Bonito, rápido, markdown |
