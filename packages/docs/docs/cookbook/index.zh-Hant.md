# 食譜概述

Panacea 食譜是一組實作指南，顯示 Panacea 平台功能的運作原理 — 文件攝取和 RAG、多代理協調、計費、MCP 工具伺服器等。每個指南指向相關的後端檔案，並解釋如何在本地運行該系統的部分。

來源: [anote-ai/Cookbook](https://github.com/anote-ai/Cookbook)。

## 食譜

| 食譜 | 描述 |
|---|---|
| [文件問答 + RAG](03-panacea-document-qa-rag.md) | 了解 Panacea 的私有文件攝取、檢索和基於事實的回答工作流程 |
| [多代理協調](04-panacea-multi-agent-orchestration.md) | 學習 Panacea 如何通過協調者、代理、團隊和工作流程來路由任務 |
| [AI 編碼工具鏈](05-panacea-ai-coding-toolchain.md) | 探索 Panacea 如何通過 CLI、VS Code 和其 SDK 提供編碼協助 |
| [多模態文件攝取](06-panacea-multimodal-ingestion.md) | 了解 Panacea 如何通過相同的 RAG 管道使圖像、音頻、視頻和電子表格可搜尋 |
| [OpenAI 兼容的 API 閘道](07-panacea-openai-compatible-gateway.md) | 將任何基於 OpenAI-SDK 的工具指向 Panacea，無需代碼更改 |
| [計費、API 金鑰與信用計量](08-panacea-billing-and-api-keys.md) | 學習 Stripe 訂閱、API 金鑰和每請求信用計量如何協同運作 |
| [MCP 工具伺服器](09-panacea-mcp-tool-server.md) | 將 Panacea 的文件/聊天原語作為標準 MCP 工具公開給 Claude Desktop 和其他 MCP 客戶端 |
| [多通道消息機器人](10-panacea-messaging-bots.md) | 從 Slack、SMS 和 WhatsApp 向 Panacea 提問編碼問題 |

## 在本地運行食譜

大多數食譜在完整的 Panacea 堆疊上運行：

```bash
cp packages/backend/.env.example packages/backend/.env
docker compose up --build
```

請參見 [開始使用](../getting-started/installation.md) 以獲取完整設置，以及每個食譜自己的頁面以獲取其特定運行步驟。
