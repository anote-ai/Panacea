# Arquitectura

## Estructura del Monorepo

```
Panacea/
├── packages/
│   ├── backend/    # Python Flask — API unificada + transmisión de agentes + RAG
│   ├── cli/        # TypeScript — terminal CLI de anote
│   ├── vscode/     # TypeScript — extensión de VS Code
│   ├── web/        # TypeScript/React — aplicación de chatbot en el navegador
│   ├── mobile/     # TypeScript/React Native (Expo) — iOS + Android
│   ├── desktop/    # TypeScript/Electron — aplicación de escritorio privada
│   ├── sdk/        # TypeScript — SDK de cliente JS/TS
│   └── docs/       # MkDocs Material — sitio de documentación
├── docker-compose.yml
├── package.json    # espacios de trabajo npm
└── Makefile
```

## Arquitectura del Backend

El backend de Python Flask maneja toda la lógica del lado del servidor:

```
packages/backend/
├── app.py                    # Punto de entrada de Flask, registro de rutas
├── api_endpoints/
│   ├── chat/                 # Transmisión de agentes (SSE), gestión de sesiones
│   ├── documents/            # Carga, pipeline RAG, preguntas y respuestas
│   ├── search/               # Consultas de índice de búsqueda semántica
│   ├── auth/                 # JWT, Google OAuth
│   ├── user/                 # Perfil, configuraciones
│   └── payments/             # Webhooks de Stripe + pago
├── agents/                   # Definiciones de agentes LangChain/LangGraph
├── services/
│   ├── rag.py                # Fragmentación de documentos + incrustaciones Chroma
│   ├── streaming.py          # Transmisión SSE a Claude/OpenAI/Gemini
│   └── search.py             # Búsqueda semántica TF-IDF
├── database/
│   ├── db.py                 # Conexión MySQL + consultas
│   └── schema.sql            # Esquema de base de datos
└── models/                   # Envolturas de proveedores de LLM
```

## Flujo de Datos: Chat de Agente

```
Cliente (CLI / VS Code / Web / Móvil)
    │  POST /api/chat/stream {mensaje, cwd, modelo}
    ▼
Backend Flask (app.py → chat/handler.py)
    │  flujo SSE
    ▼
Proveedor de LLM (Anthropic / OpenAI / Gemini / Ollama)
    │  llamadas a herramientas ↔ ejecutar (Leer/Escribir/Editar/Bash/Glob/Grep)
    ▼
Sistema de Archivos (cwd) + Chroma (contexto RAG)
```

## Elecciones Tecnológicas

| Capa | Tecnología | Por qué |
|---|---|---|
| Backend | Python Flask | Ecosistema rico en ML/IA, agentes existentes |
| Transmisión de agentes | SDK de Python de Anthropic | SSE nativo, uso de herramientas |
| DB Vectorial | ChromaDB | Local primero, sin infraestructura necesaria |
| Base de datos | MySQL | ACID, esquema existente |
| Caché | Redis | Sesión + limitación de tasa |
| Frontend | React 18 + TypeScript | Seguridad de tipos, ecosistema |
| Escritorio | Electron | Multiplataforma, empaqueta Python |
| Móvil | Expo (React Native) | Compartición de código con la web |
| CLI | Commander.js | Maduro, amigable con TypeScript |
| Docs | MkDocs Material | Hermoso, rápido, markdown |
