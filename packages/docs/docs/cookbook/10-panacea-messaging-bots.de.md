# Panacea Multi-Channel Messaging Bots

Dieses Rezept erklärt die Chat-Operations-Integrationen von Panacea: eigenständige Slack-, SMS- und WhatsApp-Bots, die es Benutzern ermöglichen, Programmierfragen aus den Messaging-Apps zu stellen, die sie bereits verwenden.

## Was Sie lernen werden

- Das gemeinsame Designmuster aller drei Bots: empfangen → rufen Sie ein LLM auf → trimmen auf das Zeichenlimit des Kanals → antworten
- Wie der Slack-Bot mit Threads umgeht und einen "denkt gerade…" Platzhalter an Ort und Stelle bearbeitet
- Wie die SMS/WhatsApp-Bots synchron mit Twilios TwiML antworten
- Eine aktuelle architektonische Lücke, die es wert ist, vor der Erweiterung dieser Bots zu kennen

## Warum das wichtig ist

Nicht jeder Benutzer möchte eine Web-UI oder IDE öffnen, um eine Frage zu stellen — Chat-Operations-Integrationen treffen die Menschen dort, wo sie bereits sind. Jeder Bot ist ein kleiner, unabhängig einsetzbarer Flask-Dienst, sodass ein Team nur die Kanäle betreiben kann, die es benötigt (z. B. nur Slack), ohne den Rest des Stacks von Panacea einzurichten.

## Wichtige Panacea-Dateien

| Datei | Warum es wichtig ist |
|---|---|
| `Panacea/packages/bots/slack/app.py` | Slack Bolt-App; unterstützt Socket Mode oder HTTP-Webhooks; threaded "denkt gerade…" Platzhalter wird an Ort und Stelle aktualisiert |
| `Panacea/packages/bots/sms/app.py` | Twilio SMS-Webhooks-Handler (`MessagingResponse`/TwiML) |
| `Panacea/packages/bots/whatsapp/app.py` | Twilio WhatsApp-Sandbox-Webhooks-Handler |
| `Panacea/packages/bots/{slack,sms,whatsapp}/.env.example` | Erforderliche Anmeldeinformationen pro Kanal |

## Wie es funktioniert

1. **Slack** (`slack/app.py`): hört auf `app_mention`-Ereignisse. `extract_query()` entfernt die `<@BOT_ID>`-Erwähnung aus dem Nachrichtentext. Es postet sofort eine `_Anote denkt gerade…_` Platzhalternachricht, führt dann den LLM-Aufruf in einem Hintergrund-Thread aus und bearbeitet entweder diesen Platzhalter an Ort und Stelle über `client.chat_update(...)` oder, wenn der Platzhalterbeitrag fehlgeschlagen ist, sendet eine frische threaded Antwort.
2. **SMS** (`sms/app.py`): Twilio POSTet jede eingehende SMS an `/sms` als Formulardaten (`Body`, `From`). Der Handler ruft das LLM synchron auf und gibt eine `MessagingResponse` (TwiML) mit der Antwort zurück — Twilio liefert sie als Folge-SMS.
3. **WhatsApp** (`whatsapp/app.py`): dasselbe TwiML-Muster wie SMS, verbunden mit Twilios WhatsApp-Sandbox-Webhooks anstelle einer Telefonnummer.
4. Alle drei rufen die **Anthropic API direkt** (`anthropic.Anthropic(...).messages.create(...)`) mit einem gemeinsamen System-Prompt auf, der Anote als Programmierassistent beschreibt — sie proxyen derzeit nicht über Panaceas eigenen Backend, sodass sie kein RAG/Dokumenten-Grundlagen, Kreditmessung oder Multi-Agenten-Orchestrierung aus den Rezepten 03/04/08 erhalten.
5. Antworten werden vor dem Senden auf das Limit jedes Kanals zugeschnitten: Slack 2900 Zeichen, SMS/WhatsApp 1600 Zeichen, jeweils mit einer Truncation-Benachrichtigung, wenn sie gekürzt werden.

### Architektonische Lücke, die es zu beachten gilt

Da diese Bots Anthropic direkt aufrufen, anstatt über Panaceas Backend zu routen, kann ein Slack/SMS/WhatsApp-Benutzer derzeit keine Fragen stellen, die auf Dokumenten basieren, die sie in Panacea hochgeladen haben, und ihre Nutzung wird nicht über das Kreditsystem im Rezept 08 gemessen. Wenn Sie Kanalparität mit der Web-UI wünschen, ist der natürliche nächste Schritt, den direkten `anthropic_client.messages.create(...)`-Aufruf gegen eine Anfrage an Panaceas eigenes `/v1/chat/completions` (Rezept 07s OpenAI-kompatibles Gateway) auszutauschen, damit diese Bots RAG, Orchestrierung und Abrechnung kostenlos erben.

## Lokal ausführen

Jeder Bot ist unabhängig — installieren und führen Sie nur die benötigten aus.

### Slack

```bash
cd Panacea/packages/bots/slack
pip install -r requirements.txt
cp .env.example .env   # füllen Sie SLACK_BOT_TOKEN, SLACK_SIGNING_SECRET, ANTHROPIC_API_KEY aus
python app.py
```

Setzen Sie `SLACK_APP_TOKEN` in `.env`, um im Socket Mode zu arbeiten (keine öffentliche URL erforderlich); andernfalls bedient es HTTP auf `PORT` (Standard 3000) und erwartet, dass Slack's Events API-Webhooks auf `POST /slack/events` zeigt.

### SMS

```bash
cd Panacea/packages/bots/sms
pip install -r requirements.txt
cp .env.example .env   # füllen Sie ANTHROPIC_API_KEY aus
python app.py
```

Konfigurieren Sie den SMS-Webhooks Ihrer Twilio-Telefonnummer auf `POST https://<your-host>/sms` (Standardport 3001).

### WhatsApp

```bash
cd Panacea/packages/bots/whatsapp
pip install -r requirements.txt
cp .env.example .env   # füllen Sie ANTHROPIC_API_KEY aus
python app.py
```

Konfigurieren Sie den Webhook Ihrer Twilio WhatsApp-Sandbox, um auf `POST /whatsapp` auf diesem Dienst zu zeigen.

Jeder Bot bietet auch `GET /health` für eine schnelle Lebenszeichenprüfung an.

## Hinweise für das Kochbuch

Dies ist ein gutes Rezept zur "Erweiterung von Panacea": Leser können sehen, wie die direkte Verbindung zu Anthropic in wenigen Minuten funktioniert, und dann der architektonischen Lückenhinweis oben folgen, um es stattdessen über Panaceas Backend zu verbinden, um fundierte, gemessene Antworten zu erhalten.
