# Aperçu du Cookbook

Le Cookbook de Panacea est un ensemble de guides d'implémentation montrant comment les fonctionnalités de la plateforme Panacea fonctionnent en coulisses — ingestion de documents et RAG, orchestration multi-agents, facturation, serveur d'outils MCP, et plus encore. Chaque guide pointe vers les véritables fichiers backend impliqués et explique comment exécuter cette partie du système localement.

Source : [anote-ai/Cookbook](https://github.com/anote-ai/Cookbook).

## Recettes

| Recette | Description |
|---|---|
| [Questions-Réponses sur les Documents + RAG](03-panacea-document-qa-rag.md) | Comprendre l'ingestion de documents privés de Panacea, la récupération et le flux de réponses ancrées |
| [Orchestration Multi-Agent](04-panacea-multi-agent-orchestration.md) | Apprendre comment Panacea achemine les tâches à travers des orchestrateurs, des agents, des équipes et des flux de travail |
| [Chaîne d'Outils de Codage AI](05-panacea-ai-coding-toolchain.md) | Explorer comment Panacea fournit une assistance au codage via CLI, VS Code et son SDK |
| [Ingestion de Documents Multi-Modal](06-panacea-multimodal-ingestion.md) | Comprendre comment Panacea rend les images, l'audio, la vidéo et les tableurs recherchables à travers le même pipeline RAG |
| [Passerelle API Compatible OpenAI](07-panacea-openai-compatible-gateway.md) | Pointer n'importe quel outil basé sur OpenAI-SDK vers Panacea sans modifications de code |
| [Facturation, Clés API & Mesure de Crédit](08-panacea-billing-and-api-keys.md) | Apprendre comment les abonnements Stripe, les clés API et la mesure de crédit par demande s'imbriquent |
| [Serveur d'Outils MCP](09-panacea-mcp-tool-server.md) | Exposer les primitives document/chat de Panacea comme outils MCP standard pour Claude Desktop et d'autres clients MCP |
| [Bots de Messagerie Multi-Canaux](10-panacea-messaging-bots.md) | Poser des questions de codage à Panacea depuis Slack, SMS et WhatsApp |

## Exécution d'une recette localement

La plupart des recettes s'exécutent contre l'ensemble de la pile Panacea :

```bash
cp packages/backend/.env.example packages/backend/.env
docker compose up --build
```

Voir [Prise en Main](../getting-started/installation.md) pour la configuration complète, et la page de chaque recette pour ses étapes d'exécution spécifiques.
