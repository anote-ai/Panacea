# 架構

## Monorepo 結構

```
Panacea/
├── packages/
│   ├── backend/    # Python Flask — 統一 API + 代理串流 + RAG
│   ├── cli/        # TypeScript — anote 終端 CLI
│   ├── vscode/     # TypeScript — VS Code 擴充功能
│   ├── web/        # TypeScript/React — 瀏覽器聊天機器人應用程式
│   ├── mobile/     # TypeScript/React Native (Expo) — iOS + Android
│   ├── desktop/    # TypeScript/Electron — 私人桌面應用程式
│   ├── sdk/        # TypeScript — JS/TS 客戶端 SDK
│   └── docs/       # MkDocs Material — 文件網站
├── docker-compose.yml
├── package.json    # npm 工作區
└── Makefile
```

## 後端架構

Python Flask 後端處理所有伺服器端邏輯：

```
packages/backend/
├── app.py                    # Flask 進入點，路由註冊
├── api_endpoints/
│   ├── chat/                 # 代理串流 (SSE)，會話管理
│   ├── documents/            # 上傳，RAG 流程，問答
│   ├── search/               # 語意搜尋索引查詢
│   ├── auth/                 # JWT，Google OAuth
│   ├── user/                 # 個人資料，設定
│   └── payments/             # Stripe 網頁鉤子 + 結帳
├── agents/                   # LangChain/LangGraph 代理定義
├── services/
│   ├── rag.py                # 文件分塊 + Chroma 嵌入
│   ├── streaming.py          # SSE 串流到 Claude/OpenAI/Gemini
│   └── search.py             # TF-IDF 語意搜尋
├── database/
│   ├── db.py                 # MySQL 連接 + 查詢
│   └── schema.sql            # 資料庫架構
└── models/                   # LLM 提供者包裝
```

## 數據流：代理聊天

```
客戶端 (CLI / VS Code / Web / Mobile)
    │  POST /api/chat/stream {message, cwd, model}
    ▼
Flask 後端 (app.py → chat/handler.py)
    │  SSE 串流
    ▼
LLM 提供者 (Anthropic / OpenAI / Gemini / Ollama)
    │  工具調用 ↔ 執行 (讀取/寫入/編輯/Bash/Glob/Grep)
    ▼
檔案系統 (cwd) + Chroma (RAG 上下文)
```

## 技術選擇

| 層級 | 技術 | 原因 |
|---|---|---|
| 後端 | Python Flask | 豐富的 ML/AI 生態系統，現有代理 |
| 代理串流 | Anthropic Python SDK | 原生 SSE，工具使用 |
| 向量資料庫 | ChromaDB | 本地優先，無需基礎設施 |
| 資料庫 | MySQL | ACID，現有架構 |
| 快取 | Redis | 會話 + 速率限制 |
| 前端 | React 18 + TypeScript | 類型安全，生態系統 |
| 桌面 | Electron | 跨平台，捆綁 Python |
| 行動 | Expo (React Native) | 與網頁共享代碼 |
| CLI | Commander.js | 成熟，TypeScript 友好 |
| 文件 | MkDocs Material | 美觀，快速，markdown |
