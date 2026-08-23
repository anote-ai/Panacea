# Panacea Document Q&A + RAG

Cette recette explique comment Panacea construit un système de questions-réponses sur des documents privés avec génération augmentée par récupération (RAG).

## Ce que vous allez apprendre

- Comment Panacea ingère des documents et les stocke en tant que texte consultable
- Comment le backend récupère des morceaux pertinents pour une question
- Comment le système utilise des embeddings et des sources de documents pour ancrer les réponses
- Comment les retours d'expérience sur les questions-réponses sont capturés et améliorent les réponses futures

## Pourquoi c'est important

Panacea est conçu pour permettre aux équipes de poser des questions sur des documents privés sans les envoyer à un service de chat tiers. Le flux de travail est :

1. Télécharger des documents
2. Découper et intégrer le contenu
3. Récupérer des morceaux pertinents pour une requête utilisateur
4. Répondre en utilisant un LLM avec des citations
5. Capturer les retours pour améliorer la qualité

## Fichiers clés de Panacea

| Fichier | Pourquoi c'est important |
|---|---|
| `Panacea/backend/api_endpoints/documents/handler.py` | Routes API pour le téléchargement et l'ingestion de documents |
| `Panacea/backend/database/db.py` | Logique SQL pour le stockage et la récupération de documents |
| `Panacea/backend/database/qa_feedback.py` | Capture des retours pour les questions-réponses sur les documents |
| `Panacea/backend/agents/multi_agent_system.py` | Agents de récupération de documents utilisés dans des flux de travail multi-agents |

## Comment ça fonctionne

- Les documents sont téléchargés via le backend et stockés dans `documents.document_text`.
- Le système découpe les grands documents et crée des métadonnées de récupération pour une recherche rapide.
- Lorsqu'un utilisateur pose une question, Panacea sélectionne un ou plusieurs agents spécialisés pour récupérer les meilleurs morceaux et génère ensuite une réponse.
- Le résultat inclut des citations de sources afin que les utilisateurs puissent retracer la réponse jusqu'au document original.
- Les signaux de retour sont enregistrés dans `qa_feedback` pour permettre des améliorations futures de la qualité.

## Exécutez-le localement

Depuis la racine de l'espace de travail (`anote/panacea`) :

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

Cela démarre le backend, l'application web, MySQL, Redis et Tika.

Si vous êtes déjà dans le dossier de la recette, utilisez :

```bash
cd ../../../Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

Ouvrez `http://localhost:3000` pour utiliser l'interface utilisateur web de Panacea. Les téléchargements de documents sont gérés par la route backend `POST /ingest-pdf` avec les champs de formulaire requis `chat_id` et `files[]`.

Exemple de commande de téléchargement :

```bash
curl -X POST http://localhost:5000/ingest-pdf \
  -F chat_id=1 \
  -F "files[]=@./path/to/document.pdf"
```

### Guide de téléchargement minimal

1. Démarrez Panacea depuis la racine du dépôt :

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

2. Dans un autre terminal, téléchargez un seul document texte ou PDF :

```bash
curl -X POST http://localhost:5000/ingest-pdf \
  -F chat_id=1 \
  -F "files[]=@./Cookbook/recipes/03-panacea-document-qa-rag/data/sample-doc.txt"
```

3. Confirmez que le backend renvoie une réponse `Document Uploaded` réussie.

4. Utilisez l'interface utilisateur web à `http://localhost:3000` et sélectionnez la même session de chat pour poser des questions sur le document téléchargé.

Si vous souhaitez tester l'API directement après le téléchargement, trouvez l'ID de session de chat dans l'interface utilisateur ou la base de données et envoyez des questions via le flux de chat de l'application. Panacea récupérera des morceaux pertinents et générera une réponse ancrée.

## Remarques pour le livre de recettes

Cette recette est idéale pour une entrée de livre de recettes qui explique comment Panacea soutient le travail de connaissance privé. Elle est plus conceptuelle qu'un script d'une ligne, car la véritable valeur réside dans la compréhension de l'architecture d'ingestion et de récupération des documents.
