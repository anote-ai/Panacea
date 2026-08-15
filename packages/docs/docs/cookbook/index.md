# Cookbook Overview

The Panacea Cookbook is a set of implementation guides showing how Panacea's platform features work under the hood — document ingestion and RAG, multi-agent orchestration, billing, the MCP tool server, and more. Each guide points at the real backend files involved and explains how to run that part of the system locally.

Source: [anote-ai/Cookbook](https://github.com/anote-ai/Cookbook).

## Recipes

| Recipe | Description |
|---|---|
| [Document Q&A + RAG](03-panacea-document-qa-rag.md) | Understand Panacea's private document ingestion, retrieval, and grounded answer workflow |
| [Multi-Agent Orchestration](04-panacea-multi-agent-orchestration.md) | Learn how Panacea routes tasks through orchestrators, agents, crews, and workflows |
| [AI Coding Toolchain](05-panacea-ai-coding-toolchain.md) | Explore how Panacea delivers coding assistance via CLI, VS Code, and its SDK |
| [Multi-Modal Document Ingestion](06-panacea-multimodal-ingestion.md) | Understand how Panacea makes images, audio, video, and spreadsheets searchable through the same RAG pipeline |
| [OpenAI-Compatible API Gateway](07-panacea-openai-compatible-gateway.md) | Point any OpenAI-SDK-based tool at Panacea with zero code changes |
| [Billing, API Keys & Credit Metering](08-panacea-billing-and-api-keys.md) | Learn how Stripe subscriptions, API keys, and per-request credit metering fit together |
| [MCP Tool Server](09-panacea-mcp-tool-server.md) | Expose Panacea's document/chat primitives as standard MCP tools for Claude Desktop and other MCP clients |
| [Multi-Channel Messaging Bots](10-panacea-messaging-bots.md) | Ask Panacea coding questions from Slack, SMS, and WhatsApp |

## Running a recipe locally

Most recipes run against the full Panacea stack:

```bash
cp packages/backend/.env.example packages/backend/.env
docker compose up --build
```

See [Getting Started](../getting-started/installation.md) for the full setup, and each recipe's own page for its specific run steps.
