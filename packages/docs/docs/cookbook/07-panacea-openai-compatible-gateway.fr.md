# Passerelle API compatible avec OpenAI de Panacea

Cette recette explique comment orienter tout outil construit contre le SDK OpenAI vers Panacea à la place — sans aucun changement de code — tout en ayant toujours accès aux extensions RAG spécifiques à Panacea comme les sources de documents ancrées.

## Ce que vous apprendrez

- Comment `AnoteOpenAI` reflète l'interface du véritable client `openai.OpenAI`
- Comment télécharger des documents et obtenir des réponses ancrées dans les documents via une API de type chat-completions
- Comment le streaming fonctionne via les événements envoyés par le serveur (SSE), à la manière d'OpenAI
- Où les extensions spécifiques à Panacea (`anote_sources`, `anote_message_id`) apparaissent dans la réponse

## Pourquoi cela est important

Une énorme quantité d'outils existants — intégrations LangChain, scripts internes, frameworks d'agents tiers — est écrite contre la structure du SDK OpenAI (`client.chat.completions.create(...)`, `client.models.list()`). Plutôt que de demander à chaque intégrateur d'apprendre un SDK Panacea sur mesure, Panacea propose un client prêt à l'emploi qui parle la même interface, permettant ainsi aux équipes d'adopter le backend privé et ancré dans les documents de Panacea sans réécrire leur code d'intégration.

## Fichiers clés de Panacea

| Fichier | Pourquoi c'est important |
|---|---|
| `Panacea/backend/sdk/anoteai/openai_compat.py` | Client `AnoteOpenAI` : `CompletionsClient`, `ModelsClient`, `DocumentsClient`, et le parseur de flux SSE |
| `Panacea/backend/sdk/anoteai/core.py` | La classe SDK sous-jacente `PrivateChatbot` que la couche de compatibilité enveloppe |
| `Panacea/backend/sdk/anoteai/handlers/private_handlers.py` | Gestion des requêtes partagée avec le SDK natif |
| Routes du serveur : `POST /v1/chat/completions`, `GET /v1/models`, `POST /v1/question-answer`, `POST /public/upload` | Les points de terminaison de type OpenAI (et un spécifique à Panacea) que le client appelle |

## Comment cela fonctionne

1. Instanciez le client exactement comme le SDK OpenAI, mais pointé vers votre backend Panacea :

   ```python
   from anoteai.openai_compat import AnoteOpenAI

   client = AnoteOpenAI(
       api_key="your-anote-api-key",       # ou définissez ANOTE_API_KEY
       base_url="http://localhost:5000",    # ou https://api.anote.ai
   )
   ```

2. Pour les questions-réponses ancrées dans les documents, téléchargez d'abord les fichiers — `client.documents.upload(...)` envoie des données de formulaire multipart à `/public/upload` et retourne un `chat_id`.
3. Posez une question de la même manière que vous appelleriez le SDK OpenAI, en passant le `chat_id` via `extra_body` afin que le serveur sache quels documents récupérer :

   ```python
   upload_resp = client.documents.upload("path/to/report.pdf")
   chat_id = upload_resp["chat_id"]

   response = client.chat.completions.create(
       model="gpt-4o",
       messages=[{"role": "user", "content": "Résumez les principales conclusions."}],
       extra_body={"chat_id": chat_id},
   )
   print(response.choices[0].message.content)
   print("Sources :", response.anote_sources)
   ```

4. La réponse est mappée dans des dataclasses qui reflètent le véritable SDK OpenAI (`ChatCompletion`, `Choice`, `Message`, `Usage`), plus deux extensions de Panacea : `anote_message_id` et `anote_sources` (les morceaux/citations récupérés soutenant la réponse).
5. Passez `stream=True` pour obtenir un générateur d'objets `ChatCompletionChunk` analysés à partir des lignes SSE `text/event-stream` (`data: {...}` par jeton, terminé par `data: [DONE]`) — la même structure que produit le client de streaming d'OpenAI.
6. `client.models.list()` appelle `GET /v1/models` pour la découverte de modèles, retournant des objets `Model`/`ModelList` tout comme le SDK OpenAI.

## Exécutez-le localement

Depuis la racine de l'espace de travail (`anote/panacea`) :

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

Installez la seule dépendance du client et définissez votre clé API :

```bash
pip install requests
export ANOTE_API_KEY=your_api_key_here   # macOS/Linux
set ANOTE_API_KEY=your_api_key_here      # Windows cmd
```

### Guide minimal

```python
from anoteai.openai_compat import AnoteOpenAI

client = AnoteOpenAI(base_url="http://localhost:5000")

# Discussion simple, sans documents :
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Quelle est la capitale de la France ?"}],
)
print(response.choices[0].message.content)

# Streaming :
for chunk in client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Comptez jusqu'à cinq."}],
    stream=True,
):
    for choice in chunk.choices:
        if choice.delta.content:
            print(choice.delta.content, end="", flush=True)
```

## Remarques pour le livre de recettes

Cette recette est un bon complément à la recette 03 — c'est la même capacité de questions-réponses/RAG sur les documents, mais exposée à travers une interface que les outils existants basés sur le SDK OpenAI peuvent consommer sans modification. Il convient de signaler aux lecteurs que `DocumentsClient.upload()`/`question_answer()` sont des helpers spécifiques à Panacea superposés au cœur compatible avec OpenAI, et ne font pas partie de la spécification OpenAI elle-même.
