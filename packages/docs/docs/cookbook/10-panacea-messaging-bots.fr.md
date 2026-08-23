# Bots de Messagerie Multi-Canaux Panacea

Cette recette explique les intégrations de style chat-ops de Panacea : des bots autonomes pour Slack, SMS et WhatsApp qui permettent aux utilisateurs de poser des questions de codage depuis les applications de messagerie qu'ils utilisent déjà.

## Ce que vous allez apprendre

- Le modèle de conception partagé entre les trois bots : recevoir → appeler un LLM → réduire à la limite de caractères du canal → répondre
- Comment le bot Slack gère le fil de discussion et édite un message de remplacement "en train de réfléchir…"
- Comment les bots SMS/WhatsApp répondent de manière synchrone en utilisant Twilio's TwiML
- Un écart architectural actuel qu'il vaut la peine de connaître avant d'étendre ces bots

## Pourquoi cela importe

Tous les utilisateurs ne souhaitent pas ouvrir une interface web ou un IDE pour poser une question — les intégrations de style chat-ops rencontrent les gens là où ils se trouvent déjà. Chaque bot est un petit service Flask déployable indépendamment, donc une équipe peut faire fonctionner uniquement les canaux dont elle a besoin (par exemple, uniquement Slack) sans déployer le reste de la pile de Panacea.

## Fichiers clés de Panacea

| Fichier | Pourquoi cela importe |
|---|---|
| `Panacea/packages/bots/slack/app.py` | Application Slack Bolt ; prend en charge le mode Socket ou le webhook HTTP ; message de remplacement "en train de réfléchir…" mis à jour sur place |
| `Panacea/packages/bots/sms/app.py` | Gestionnaire de webhook SMS Twilio (`MessagingResponse`/TwiML) |
| `Panacea/packages/bots/whatsapp/app.py` | Gestionnaire de webhook WhatsApp sandbox de Twilio |
| `Panacea/packages/bots/{slack,sms,whatsapp}/.env.example` | Identifiants requis par canal |

## Comment cela fonctionne

1. **Slack** (`slack/app.py`) : écoute les événements `app_mention`. `extract_query()` extrait la mention `<@BOT_ID>` du texte du message. Il poste immédiatement un message de remplacement `_Anote est en train de réfléchir…_`, puis exécute l'appel LLM dans un thread en arrière-plan et édite soit ce message de remplacement sur place via `client.chat_update(...)`, soit, si la publication du message de remplacement a échoué, envoie une nouvelle réponse en fil de discussion.
2. **SMS** (`sms/app.py`) : Twilio envoie chaque texte entrant à `/sms` en tant que données de formulaire (`Body`, `From`). Le gestionnaire appelle le LLM de manière synchrone et renvoie un `MessagingResponse` (TwiML) avec la réponse — Twilio le livre en tant que texte de suivi.
3. **WhatsApp** (`whatsapp/app.py`) : même modèle TwiML que SMS, connecté au webhook sandbox WhatsApp de Twilio au lieu d'un numéro de téléphone.
4. Les trois appellent directement l'**API Anthropic** (`anthropic.Anthropic(...).messages.create(...)`) avec un prompt système partagé décrivant Anote comme un assistant de codage — elles ne passent actuellement pas par le backend de Panacea, donc elles ne bénéficient pas de RAG/grounding de documents, de mesure de crédits, ou d'orchestration multi-agents des recettes 03/04/08.
5. Les réponses sont réduites à la limite de chaque canal avant l'envoi : Slack 2900 caractères, SMS/WhatsApp 1600 caractères, chacune avec un avis de troncature ajouté si coupée.

### Écart architectural à connaître

Parce que ces bots appellent Anthropic directement au lieu de passer par le backend de Panacea, un utilisateur Slack/SMS/WhatsApp ne peut actuellement pas poser de questions ancrées dans des documents qu'il a téléchargés sur Panacea, et leur utilisation n'est pas mesurée par le système de crédits dans la recette 08. Si vous souhaitez une parité de canal avec l'interface web, la prochaine étape naturelle est de remplacer l'appel direct `anthropic_client.messages.create(...)` par une requête vers le propre `/v1/chat/completions` de Panacea (la passerelle compatible OpenAI de la recette 07) afin que ces bots héritent de RAG, d'orchestration et de facturation gratuitement.

## Exécutez-le localement

Chaque bot est indépendant — installez et exécutez uniquement ceux dont vous avez besoin.

### Slack

```bash
cd Panacea/packages/bots/slack
pip install -r requirements.txt
cp .env.example .env   # remplissez SLACK_BOT_TOKEN, SLACK_SIGNING_SECRET, ANTHROPIC_API_KEY
python app.py
```

Définissez `SLACK_APP_TOKEN` dans `.env` pour exécuter en mode Socket (aucune URL publique nécessaire) ; sinon, il sert HTTP sur `PORT` (par défaut 3000) et attend que le webhook de l'API des événements de Slack pointe vers `POST /slack/events`.

### SMS

```bash
cd Panacea/packages/bots/sms
pip install -r requirements.txt
cp .env.example .env   # remplissez ANTHROPIC_API_KEY
python app.py
```

Configurez le webhook SMS de votre numéro de téléphone Twilio pour `POST https://<your-host>/sms` (port par défaut 3001).

### WhatsApp

```bash
cd Panacea/packages/bots/whatsapp
pip install -r requirements.txt
cp .env.example .env   # remplissez ANTHROPIC_API_KEY
python app.py
```

Configurez le webhook sandbox WhatsApp de Twilio pour pointer vers `POST /whatsapp` sur ce service.

Chaque bot expose également `GET /health` pour un contrôle rapide de l'état.

## Notes pour le livre de recettes

C'est une bonne recette pour "étendre Panacea" : les lecteurs peuvent voir la version directe vers Anthropic fonctionner en quelques minutes, puis suivre la note sur l'écart architectural ci-dessus pour la connecter au backend de Panacea à la place pour des réponses ancrées et mesurées.
