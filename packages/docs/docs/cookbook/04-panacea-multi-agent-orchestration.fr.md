# Orchestration Multi-Agent de Panacea

Cette recette explique l'architecture d'orchestration des agents de Panacea : comment l'orchestrateur attribue des tâches, choisit des agents et prend en charge des flux de travail séquentiels et hiérarchiques.

## Ce que vous apprendrez

- Le rôle de l'orchestrateur en tant que cerveau du système
- Comment Panacea achemine les tâches vers des agents spécialisés
- La différence entre les flux de travail séquentiels et hiérarchiques
- Comment les équipes d'agents collaborent sur un objectif commun
- Comment fonctionne l'enregistrement des outils afin que les agents puissent utiliser de nouvelles capacités

## Pourquoi cela importe

Dans Panacea, l'orchestrateur n'est pas aléatoire. Il choisit le meilleur agent en fonction des descriptions de capacité, du contexte de la tâche et de l'état du flux de travail. Cela rend le système prévisible et extensible.

## Concepts clés

- **Orchestrateur** — coordinateur central qui décide quel agent s'exécute ensuite
- **Agent** — unité autonome avec un but défini, tel que `DocumentRetrievalAgent`, `GeneralKnowledgeAgent` ou `ChatHistoryAgent`
- **Équipe** — un groupe d'agents travaillant ensemble vers un objectif commun
- **Flux de travail** — le style de collaboration ; peut être :
  - **Séquentiel** : une étape suit une autre dans l'ordre
  - **Hiérarchique** : une chaîne de commandement où l'orchestrateur délègue des sous-tâches à des spécialistes
- **Outils** — fonctions que les agents peuvent appeler pour effectuer des actions comme rechercher, télécharger ou exécuter du code

## Fichiers clés de Panacea

| Fichier | Pourquoi cela importe |
|---|---|
| `Panacea/backend/agents/multi_agent_system.py` | Logique d'orchestrateur et de routage des flux de travail |
| `Panacea/backend/agents/autonomous_agent.py` | Enregistrement des outils et cycle de vie des agents |
| `Panacea/backend/agents/routing.py` | Logique d'assistance au routage des tâches |
| `Panacea/backend/agents/reactive_agent.py` | Initialise le système multi-agent et le connecte aux flux de chat |

## Comment cela fonctionne

1. Un utilisateur soumet une tâche ou une requête.
2. L'agent orchestrateur examine l'entrée et choisit un agent suivant en fonction des capacités et des exigences de la tâche.
3. Les agents spécialisés exécutent leur part du pipeline et peuvent renvoyer des résultats intermédiaires.
4. L'orchestrateur peut soit continuer séquentiellement, soit continuer à déléguer des sous-tâches dans un modèle hiérarchique.
5. Le résultat final est assemblé et renvoyé à l'utilisateur.

### Flux de travail séquentiel

Un flux de travail séquentiel est utile pour des pipelines fixes tels que :

- récupérer des morceaux de document → résumer → répondre à l'utilisateur
- rassembler le contexte du code → analyser le code → renvoyer des suggestions de révision

Chaque étape s'exécute dans l'ordre, et l'étape suivante utilise la sortie de l'étape précédente.

### Flux de travail hiérarchique

Un flux de travail hiérarchique est utile pour des tâches complexes où l'orchestrateur gère des spécialistes :

- l'orchestrateur attribue un agent pour rassembler des données
- un autre agent valide les données
- un troisième agent génère la réponse finale

C'est similaire à une chaîne de commandement : l'orchestrateur reste en contrôle et délègue le travail à des agents spécialisés.

## Enregistrement des outils

Panacea prend en charge l'enregistrement dynamique des outils. Si un agent a besoin d'une nouvelle capacité, il peut appeler `register_tool(...)` depuis `backend/agents/autonomous_agent.py`.

Cela signifie que le livre de recettes peut documenter non seulement comment utiliser les outils existants, mais aussi comment ajouter de nouveaux outils au système.

## Boucle de rétroaction

Les retours des utilisateurs sont essentiels pour améliorer la sélection des agents. Panacea enregistre les retours des questions-réponses sur les documents et les résultats des tâches afin que l'orchestrateur puisse apprendre quels agents et outils produisent les meilleurs résultats.

## Remarques pour le livre de recettes

Cette recette est un fort candidat pour une explication manuelle. Elle devrait inclure des diagrammes ou des exemples de flux étape par étape qui montrent pourquoi l'orchestrateur prend des décisions au lieu de laisser la sélection des agents au hasard.
