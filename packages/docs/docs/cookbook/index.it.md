# Panoramica del Cookbook

Il Cookbook di Panacea è un insieme di guide all'implementazione che mostrano come funzionano le funzionalità della piattaforma di Panacea — ingestione dei documenti e RAG, orchestrazione multi-agente, fatturazione, il server degli strumenti MCP e altro ancora. Ogni guida indica i veri file di backend coinvolti e spiega come eseguire quella parte del sistema localmente.

Fonte: [anote-ai/Cookbook](https://github.com/anote-ai/Cookbook).

## Ricette

| Ricetta | Descrizione |
|---|---|
| [Domande e Risposte sui Documenti + RAG](03-panacea-document-qa-rag.md) | Comprendere l'ingestione, il recupero e il flusso di lavoro delle risposte fondate sui documenti privati di Panacea |
| [Orchestrazione Multi-Agent](04-panacea-multi-agent-orchestration.md) | Scoprire come Panacea instrada i compiti attraverso orchestratori, agenti, squadre e flussi di lavoro |
| [Toolchain di Codifica AI](05-panacea-ai-coding-toolchain.md) | Esplora come Panacea fornisce assistenza alla codifica tramite CLI, VS Code e il suo SDK |
| [Ingestione Documentale Multi-Modale](06-panacea-multimodal-ingestion.md) | Comprendere come Panacea rende ricercabili immagini, audio, video e fogli di calcolo attraverso lo stesso pipeline RAG |
| [Gateway API Compatibile con OpenAI](07-panacea-openai-compatible-gateway.md) | Puntare qualsiasi strumento basato su OpenAI-SDK a Panacea senza modifiche al codice |
| [Fatturazione, Chiavi API e Misurazione del Credito](08-panacea-billing-and-api-keys.md) | Scoprire come si integrano gli abbonamenti Stripe, le chiavi API e la misurazione del credito per richiesta |
| [Server degli Strumenti MCP](09-panacea-mcp-tool-server.md) | Esporre le primitive di documento/chat di Panacea come strumenti MCP standard per Claude Desktop e altri client MCP |
| [Bot di Messaggistica Multi-Canale](10-panacea-messaging-bots.md) | Porre domande di codifica a Panacea tramite Slack, SMS e WhatsApp |

## Esecuzione di una ricetta localmente

La maggior parte delle ricette viene eseguita contro l'intero stack di Panacea:

```bash
cp packages/backend/.env.example packages/backend/.env
docker compose up --build
```

Consulta [Iniziare](../getting-started/installation.md) per la configurazione completa e la pagina specifica di ciascuna ricetta per i suoi passaggi di esecuzione specifici.
