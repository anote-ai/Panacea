# 架构

## Monorepo 结构

```
Panacea/
├── packages/
│   ├── backend/    # Python Flask — 统一 API + 代理流 + RAG
│   ├── cli/        # TypeScript — anote 终端 CLI
│   ├── vscode/     # TypeScript — VS Code 扩展
│   ├── web/        # TypeScript/React — 浏览器聊天机器人应用
│   ├── mobile/     # TypeScript/React Native (Expo) — iOS + Android
│   ├── desktop/    # TypeScript/Electron — 私有桌面应用
│   ├── sdk/        # TypeScript — JS/TS 客户端 SDK
│   └── docs/       # MkDocs Material — 文档网站
├── docker-compose.yml
├── package.json    # npm 工作区
└── Makefile
```

## 后端架构

Python Flask 后端处理所有服务器端逻辑：

```
packages/backend/
├── app.py                    # Flask 入口点，路由注册
├── api_endpoints/
│   ├── chat/                 # 代理流 (SSE)，会话管理
│   ├── documents/            # 上传，RAG 流程，问答
│   ├── search/               # 语义搜索索引查询
│   ├── auth/                 # JWT，Google OAuth
│   ├── user/                 # 个人资料，设置
│   └── payments/             # Stripe 网络钩子 + 结账
├── agents/                   # LangChain/LangGraph 代理定义
├── services/
│   ├── rag.py                # 文档分块 + Chroma 嵌入
│   ├── streaming.py          # SSE 流向 Claude/OpenAI/Gemini
│   └── search.py             # TF-IDF 语义搜索
├── database/
│   ├── db.py                 # MySQL 连接 + 查询
│   └── schema.sql            # 数据库模式
└── models/                   # LLM 提供者包装
```

## 数据流：代理聊天

```
客户端 (CLI / VS Code / Web / Mobile)
    │  POST /api/chat/stream {message, cwd, model}
    ▼
Flask 后端 (app.py → chat/handler.py)
    │  SSE 流
    ▼
LLM 提供者 (Anthropic / OpenAI / Gemini / Ollama)
    │  工具调用 ↔ 执行 (读取/写入/编辑/Bash/Glob/Grep)
    ▼
文件系统 (cwd) + Chroma (RAG 上下文)
```

## 技术选择

| 层级 | 技术 | 原因 |
|---|---|---|
| 后端 | Python Flask | 丰富的 ML/AI 生态系统，现有代理 |
| 代理流 | Anthropic Python SDK | 原生 SSE，工具使用 |
| 向量数据库 | ChromaDB | 本地优先，无需基础设施 |
| 数据库 | MySQL | ACID，现有模式 |
| 缓存 | Redis | 会话 + 速率限制 |
| 前端 | React 18 + TypeScript | 类型安全，生态系统 |
| 桌面 | Electron | 跨平台，捆绑 Python |
| 移动 | Expo (React Native) | 与网页共享代码 |
| CLI | Commander.js | 成熟，TypeScript 友好 |
| 文档 | MkDocs Material | 美观，快速，markdown |
