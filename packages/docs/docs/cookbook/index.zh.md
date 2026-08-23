# 食谱概述

Panacea 食谱是一些实施指南，展示了 Panacea 平台功能的内部工作原理——文档摄取和 RAG、多代理编排、计费、MCP 工具服务器等。每个指南指向相关的后端文件，并解释如何在本地运行系统的该部分。

来源: [anote-ai/Cookbook](https://github.com/anote-ai/Cookbook)。

## 食谱

| 食谱 | 描述 |
|---|---|
| [文档问答 + RAG](03-panacea-document-qa-rag.md) | 了解 Panacea 的私有文档摄取、检索和基于事实的回答工作流程 |
| [多代理编排](04-panacea-multi-agent-orchestration.md) | 学习 Panacea 如何通过编排者、代理、团队和工作流路由任务 |
| [AI 编码工具链](05-panacea-ai-coding-toolchain.md) | 探索 Panacea 如何通过 CLI、VS Code 和其 SDK 提供编码帮助 |
| [多模态文档摄取](06-panacea-multimodal-ingestion.md) | 了解 Panacea 如何通过相同的 RAG 管道使图像、音频、视频和电子表格可搜索 |
| [与 OpenAI 兼容的 API 网关](07-panacea-openai-compatible-gateway.md) | 将任何基于 OpenAI-SDK 的工具指向 Panacea，无需代码更改 |
| [计费、API 密钥和按请求计费](08-panacea-billing-and-api-keys.md) | 了解 Stripe 订阅、API 密钥和按请求计费如何结合在一起 |
| [MCP 工具服务器](09-panacea-mcp-tool-server.md) | 将 Panacea 的文档/聊天原语暴露为 Claude Desktop 和其他 MCP 客户端的标准 MCP 工具 |
| [多渠道消息机器人](10-panacea-messaging-bots.md) | 从 Slack、SMS 和 WhatsApp 向 Panacea 提问编码问题 |

## 在本地运行食谱

大多数食谱在完整的 Panacea 堆栈上运行：

```bash
cp packages/backend/.env.example packages/backend/.env
docker compose up --build
```

请参阅 [入门](../getting-started/installation.md) 以获取完整的设置，以及每个食谱自己的页面以获取其特定的运行步骤。
