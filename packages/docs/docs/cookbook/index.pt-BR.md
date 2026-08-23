# Visão Geral do Cookbook

O Cookbook da Panacea é um conjunto de guias de implementação que mostram como as funcionalidades da plataforma Panacea funcionam internamente — ingestão de documentos e RAG, orquestração multi-agente, faturamento, o servidor de ferramentas MCP e mais. Cada guia aponta para os arquivos de backend reais envolvidos e explica como executar essa parte do sistema localmente.

Fonte: [anote-ai/Cookbook](https://github.com/anote-ai/Cookbook).

## Receitas

| Receita | Descrição |
|---|---|
| [Perguntas e Respostas sobre Documentos + RAG](03-panacea-document-qa-rag.md) | Entenda a ingestão de documentos privados da Panacea, recuperação e fluxo de respostas fundamentadas |
| [Orquestração Multi-Agent](04-panacea-multi-agent-orchestration.md) | Aprenda como a Panacea roteia tarefas através de orquestradores, agentes, equipes e fluxos de trabalho |
| [Ferramenta de Codificação de IA](05-panacea-ai-coding-toolchain.md) | Explore como a Panacea oferece assistência de codificação via CLI, VS Code e seu SDK |
| [Ingestão de Documentos Multi-Modal](06-panacea-multimodal-ingestion.md) | Entenda como a Panacea torna imagens, áudio, vídeo e planilhas pesquisáveis através do mesmo pipeline RAG |
| [Gateway de API Compatível com OpenAI](07-panacea-openai-compatible-gateway.md) | Aponte qualquer ferramenta baseada no OpenAI-SDK para a Panacea sem alterações de código |
| [Faturamento, Chaves de API e Medição de Crédito](08-panacea-billing-and-api-keys.md) | Aprenda como assinaturas do Stripe, chaves de API e medição de crédito por solicitação se encaixam |
| [Servidor de Ferramentas MCP](09-panacea-mcp-tool-server.md) | Exponha os primitivos de documento/chat da Panacea como ferramentas MCP padrão para Claude Desktop e outros clientes MCP |
| [Bots de Mensagens Multi-Canal](10-panacea-messaging-bots.md) | Faça perguntas de codificação para a Panacea via Slack, SMS e WhatsApp |

## Executando uma receita localmente

A maioria das receitas é executada contra toda a pilha da Panacea:

```bash
cp packages/backend/.env.example packages/backend/.env
docker compose up --build
```

Veja [Introdução](../getting-started/installation.md) para a configuração completa, e a página de cada receita para seus passos específicos de execução.
