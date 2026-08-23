# Arsitektur

## Struktur Monorepo

```
Panacea/
├── packages/
│   ├── backend/    # Python Flask — API terpadu + streaming agen + RAG
│   ├── cli/        # TypeScript — terminal CLI anote
│   ├── vscode/     # TypeScript — ekstensi VS Code
│   ├── web/        # TypeScript/React — aplikasi chatbot browser
│   ├── mobile/     # TypeScript/React Native (Expo) — iOS + Android
│   ├── desktop/    # TypeScript/Electron — aplikasi desktop pribadi
│   ├── sdk/        # TypeScript — SDK klien JS/TS
│   └── docs/       # MkDocs Material — situs dokumentasi
├── docker-compose.yml
├── package.json    # npm workspaces
└── Makefile
```

## Arsitektur Backend

Backend Python Flask menangani semua logika sisi server:

```
packages/backend/
├── app.py                    # Titik masuk Flask, pendaftaran rute
├── api_endpoints/
│   ├── chat/                 # Streaming agen (SSE), manajemen sesi
│   ├── documents/            # Unggah, pipeline RAG, Q&A
│   ├── search/               # Kuery indeks pencarian semantik
│   ├── auth/                 # JWT, Google OAuth
│   ├── user/                 # Profil, pengaturan
│   └── payments/             # Webhook Stripe + checkout
├── agents/                   # Definisi agen LangChain/LangGraph
├── services/
│   ├── rag.py                # Pemotongan dokumen + embedding Chroma
│   ├── streaming.py          # Streaming SSE ke Claude/OpenAI/Gemini
│   └── search.py             # Pencarian semantik TF-IDF
├── database/
│   ├── db.py                 # Koneksi MySQL + kueri
│   └── schema.sql            # Skema basis data
└── models/                   # Pembungkus penyedia LLM
```

## Alur Data: Obrolan Agen

```
Klien (CLI / VS Code / Web / Mobile)
    │  POST /api/chat/stream {message, cwd, model}
    ▼
Backend Flask (app.py → chat/handler.py)
    │  streaming SSE
    ▼
Penyedia LLM (Anthropic / OpenAI / Gemini / Ollama)
    │  panggilan alat ↔ eksekusi (Baca/Tulis/Edit/Bash/Glob/Grep)
    ▼
Sistem Berkas (cwd) + Chroma (konteks RAG)
```

## Pilihan Teknologi

| Lapisan | Teknologi | Mengapa |
|---|---|---|
| Backend | Python Flask | Ekosistem ML/AI yang kaya, agen yang ada |
| Streaming agen | Anthropic Python SDK | SSE native, penggunaan alat |
| DB Vektor | ChromaDB | Local-first, tanpa infrastruktur yang dibutuhkan |
| Basis Data | MySQL | ACID, skema yang ada |
| Cache | Redis | Sesi + pembatasan laju |
| Frontend | React 18 + TypeScript | Keamanan tipe, ekosistem |
| Desktop | Electron | Lintas platform, mengemas Python |
| Mobile | Expo (React Native) | Berbagi kode dengan web |
| CLI | Commander.js | Matang, ramah TypeScript |
| Dokumen | MkDocs Material | Indah, cepat, markdown |
