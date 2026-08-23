# Descripción general del Cookbook

El Cookbook de Panacea es un conjunto de guías de implementación que muestran cómo funcionan las características de la plataforma de Panacea en el fondo: ingestión de documentos y RAG, orquestación de múltiples agentes, facturación, el servidor de herramientas MCP y más. Cada guía señala los archivos de backend reales involucrados y explica cómo ejecutar esa parte del sistema localmente.

Fuente: [anote-ai/Cookbook](https://github.com/anote-ai/Cookbook).

## Recetas

| Receta | Descripción |
|---|---|
| [Document Q&A + RAG](03-panacea-document-qa-rag.md) | Comprender la ingestión de documentos privados de Panacea, la recuperación y el flujo de trabajo de respuestas fundamentadas |
| [Orquestación de Múltiples Agentes](04-panacea-multi-agent-orchestration.md) | Aprender cómo Panacea enruta tareas a través de orquestadores, agentes, equipos y flujos de trabajo |
| [Cadena de Herramientas de Codificación AI](05-panacea-ai-coding-toolchain.md) | Explorar cómo Panacea ofrece asistencia de codificación a través de CLI, VS Code y su SDK |
| [Ingestión de Documentos Multimodal](06-panacea-multimodal-ingestion.md) | Comprender cómo Panacea hace que imágenes, audio, video y hojas de cálculo sean buscables a través del mismo pipeline RAG |
| [Puerta de Enlace API Compatible con OpenAI](07-panacea-openai-compatible-gateway.md) | Apuntar cualquier herramienta basada en OpenAI-SDK a Panacea sin cambios en el código |
| [Facturación, Claves API y Medición de Créditos](08-panacea-billing-and-api-keys.md) | Aprender cómo se integran las suscripciones de Stripe, las claves API y la medición de créditos por solicitud |
| [Servidor de Herramientas MCP](09-panacea-mcp-tool-server.md) | Exponer las primitivas de documento/chat de Panacea como herramientas MCP estándar para Claude Desktop y otros clientes MCP |
| [Bots de Mensajería Multicanal](10-panacea-messaging-bots.md) | Hacer preguntas de codificación a Panacea desde Slack, SMS y WhatsApp |

## Ejecutando una receta localmente

La mayoría de las recetas se ejecutan contra toda la pila de Panacea:

```bash
cp packages/backend/.env.example packages/backend/.env
docker compose up --build
```

Consulta [Introducción](../getting-started/installation.md) para la configuración completa, y la página de cada receta para sus pasos específicos de ejecución.
