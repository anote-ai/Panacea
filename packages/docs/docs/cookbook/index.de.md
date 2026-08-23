# Kochbuch Übersicht

Das Panacea Kochbuch ist eine Sammlung von Implementierungsanleitungen, die zeigen, wie die Funktionen der Panacea-Plattform im Hintergrund funktionieren — Dokumentenaufnahme und RAG, Multi-Agenten-Orchestrierung, Abrechnung, der MCP-Tool-Server und mehr. Jede Anleitung verweist auf die tatsächlichen Backend-Dateien, die beteiligt sind, und erklärt, wie man diesen Teil des Systems lokal ausführt.

Quelle: [anote-ai/Cookbook](https://github.com/anote-ai/Cookbook).

## Rezepte

| Rezept | Beschreibung |
|---|---|
| [Dokument Q&A + RAG](03-panacea-document-qa-rag.md) | Verstehen Sie die private Dokumentenaufnahme, Abruf und den verankerten Antwort-Workflow von Panacea |
| [Multi-Agenten-Orchestrierung](04-panacea-multi-agent-orchestration.md) | Lernen Sie, wie Panacea Aufgaben durch Orchestratoren, Agenten, Crews und Workflows leitet |
| [AI Coding Toolchain](05-panacea-ai-coding-toolchain.md) | Erkunden Sie, wie Panacea Programmierhilfe über CLI, VS Code und sein SDK bereitstellt |
| [Multi-Modale Dokumentenaufnahme](06-panacea-multimodal-ingestion.md) | Verstehen Sie, wie Panacea Bilder, Audio, Video und Tabellenkalkulationen durch dasselbe RAG-Pipeline durchsuchbar macht |
| [OpenAI-kompatibles API-Gateway](07-panacea-openai-compatible-gateway.md) | Richten Sie jedes OpenAI-SDK-basiertes Tool auf Panacea ohne Codeänderungen aus |
| [Abrechnung, API-Schlüssel & Kreditabrechnung](08-panacea-billing-and-api-keys.md) | Lernen Sie, wie Stripe-Abonnements, API-Schlüssel und die Kreditabrechnung pro Anfrage zusammenpassen |
| [MCP Tool Server](09-panacea-mcp-tool-server.md) | Stellen Sie die Dokument-/Chat-Primitiven von Panacea als standardmäßige MCP-Tools für Claude Desktop und andere MCP-Clients bereit |
| [Multi-Channel Messaging Bots](10-panacea-messaging-bots.md) | Stellen Sie Panacea Programmierfragen über Slack, SMS und WhatsApp |

## Ein Rezept lokal ausführen

Die meisten Rezepte laufen gegen den vollständigen Panacea-Stack:

```bash
cp packages/backend/.env.example packages/backend/.env
docker compose up --build
```

Siehe [Erste Schritte](../getting-started/installation.md) für die vollständige Einrichtung und die eigene Seite jedes Rezepts für die spezifischen Ausführungsschritte.
