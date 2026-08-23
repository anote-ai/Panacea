# Panacea Bot di Messaggistica Multi-Canale

Questa ricetta spiega le integrazioni in stile chat-ops di Panacea: bot autonomi per Slack, SMS e WhatsApp che consentono agli utenti di porre domande di programmazione dalle app di messaggistica che già utilizzano.

## Cosa imparerai

- Il modello di design condiviso tra tutti e tre i bot: ricevi → chiama un LLM → riduci al limite di caratteri del canale → rispondi
- Come il bot di Slack gestisce i thread e modifica un segnaposto "sto pensando…" in loco
- Come i bot SMS/WhatsApp rispondono in modo sincrono utilizzando il TwiML di Twilio
- Un attuale gap architetturale che vale la pena conoscere prima di estendere questi bot

## Perché è importante

Non tutti gli utenti vogliono aprire un'interfaccia web o un IDE per porre una domanda: le integrazioni in stile chat-ops incontrano le persone dove si trovano già. Ogni bot è un piccolo servizio Flask indipendentemente distribuibile, quindi un team può eseguire solo i canali di cui ha bisogno (ad esempio, solo Slack) senza dover attivare il resto dello stack di Panacea.

## File chiave di Panacea

| File | Perché è importante |
|---|---|
| `Panacea/packages/bots/slack/app.py` | App Slack Bolt; supporta Socket Mode o webhook HTTP; segnaposto "sto pensando…" aggiornato in loco |
| `Panacea/packages/bots/sms/app.py` | Gestore webhook SMS di Twilio (`MessagingResponse`/TwiML) |
| `Panacea/packages/bots/whatsapp/app.py` | Gestore webhook sandbox WhatsApp di Twilio |
| `Panacea/packages/bots/{slack,sms,whatsapp}/.env.example` | Credenziali richieste per canale |

## Come funziona

1. **Slack** (`slack/app.py`): ascolta gli eventi `app_mention`. `extract_query()` rimuove la menzione `<@BOT_ID>` dal testo del messaggio. Pubblica immediatamente un messaggio segnaposto `_Anote sta pensando…_`, quindi esegue la chiamata LLM in un thread in background e modifica quel segnaposto in loco tramite `client.chat_update(...)` oppure, se il post del segnaposto è fallito, invia una nuova risposta in thread.
2. **SMS** (`sms/app.py`): Twilio invia ogni messaggio di testo in entrata a `/sms` come dati di modulo (`Body`, `From`). Il gestore chiama il LLM in modo sincrono e restituisce un `MessagingResponse` (TwiML) con la risposta — Twilio lo consegna come messaggio di follow-up.
3. **WhatsApp** (`whatsapp/app.py`): stesso modello TwiML come SMS, collegato al webhook sandbox WhatsApp di Twilio invece di un numero di telefono.
4. Tutti e tre chiamano direttamente l'**API di Anthropic** (`anthropic.Anthropic(...).messages.create(...)`) con un prompt di sistema condiviso che descrive Anote come assistente alla programmazione — attualmente non fanno proxy attraverso il backend di Panacea, quindi non ottengono RAG/grounding dei documenti, misurazione dei crediti o orchestrazione multi-agente dalle ricette 03/04/08.
5. Le risposte vengono ridotte al limite di ciascun canale prima di essere inviate: Slack 2900 caratteri, SMS/WhatsApp 1600 caratteri, ciascuna con un avviso di troncamento aggiunto se tagliata.

### Gap architetturale da conoscere

Poiché questi bot chiamano direttamente Anthropic invece di instradare attraverso il backend di Panacea, un utente di Slack/SMS/WhatsApp non può attualmente porre domande basate su documenti che ha caricato su Panacea, e il loro utilizzo non è misurato attraverso il sistema di crediti nella ricetta 08. Se desideri parità di canale con l'interfaccia web, il passo successivo naturale è sostituire la chiamata diretta `anthropic_client.messages.create(...)` con una richiesta al proprio `/v1/chat/completions` di Panacea (gateway compatibile con OpenAI della ricetta 07) in modo che questi bot ereditino RAG, orchestrazione e fatturazione gratuitamente.

## Esegui localmente

Ogni bot è indipendente: installa ed esegui solo quelli di cui hai bisogno.

### Slack

```bash
cd Panacea/packages/bots/slack
pip install -r requirements.txt
cp .env.example .env   # compila SLACK_BOT_TOKEN, SLACK_SIGNING_SECRET, ANTHROPIC_API_KEY
python app.py
```

Imposta `SLACK_APP_TOKEN` in `.env` per eseguire in Socket Mode (non è necessaria un'URL pubblica); altrimenti serve HTTP su `PORT` (default 3000) e si aspetta che il webhook dell'API Eventi di Slack punti a `POST /slack/events`.

### SMS

```bash
cd Panacea/packages/bots/sms
pip install -r requirements.txt
cp .env.example .env   # compila ANTHROPIC_API_KEY
python app.py
```

Configura il webhook SMS del tuo numero di telefono Twilio su `POST https://<your-host>/sms` (porta predefinita 3001).

### WhatsApp

```bash
cd Panacea/packages/bots/whatsapp
pip install -r requirements.txt
cp .env.example .env   # compila ANTHROPIC_API_KEY
python app.py
```

Configura il webhook sandbox WhatsApp di Twilio per puntare a `POST /whatsapp` su questo servizio.

Ogni bot espone anche `GET /health` per un rapido controllo di vitalità.

## Note per il ricettario

Questa è una buona ricetta per "estendere Panacea": i lettori possono vedere la versione diretta su Anthropic funzionare in pochi minuti, quindi seguire la nota sul gap architetturale sopra per collegarla attraverso il backend di Panacea invece per risposte basate su documenti e misurate.
