# Panacea Document Q&A + RAG

Questa ricetta spiega come Panacea costruisce un sistema di domande e risposte su documenti privati con generazione aumentata da recupero (RAG).

## Cosa imparerai

- Come Panacea acquisisce documenti e li memorizza come testo ricercabile
- Come il backend recupera frammenti rilevanti per una domanda
- Come il sistema utilizza embedding e fonti documentali per fondare le risposte
- Come il feedback delle domande e risposte viene catturato e migliora le risposte future

## Perché è importante

Panacea è progettato per consentire ai team di porre domande su documenti privati senza inviarli a un servizio di chat di terze parti. Il flusso di lavoro è:

1. Carica documenti
2. Frammenta e incorpora contenuti
3. Recupera frammenti rilevanti per una query dell'utente
4. Rispondi utilizzando un LLM con citazioni
5. Cattura feedback per migliorare la qualità

## File chiave di Panacea

| File | Perché è importante |
|---|---|
| `Panacea/backend/api_endpoints/documents/handler.py` | Percorsi API per il caricamento e l'acquisizione dei documenti |
| `Panacea/backend/database/db.py` | Logica SQL per la memorizzazione e il recupero dei documenti |
| `Panacea/backend/database/qa_feedback.py` | Cattura del feedback per le domande e risposte sui documenti |
| `Panacea/backend/agents/multi_agent_system.py` | Agenti di recupero documenti utilizzati nei flussi di lavoro multi-agente |

## Come funziona

- I documenti vengono caricati tramite il backend e memorizzati in `documents.document_text`.
- Il sistema frammenta documenti di grandi dimensioni e crea metadati di recupero per una ricerca rapida.
- Quando un utente pone una domanda, Panacea seleziona uno o più agenti specializzati per recuperare i migliori frammenti e poi genera una risposta.
- Il risultato include citazioni delle fonti in modo che gli utenti possano risalire alla risposta originale.
- I segnali di feedback vengono registrati in `qa_feedback` per abilitare futuri miglioramenti della qualità.

## Esegui localmente

Dalla radice del workspace (`anote/panacea`):

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

Questo avvia il backend, l'app web, MySQL, Redis e Tika.

Se sei già dentro la cartella della ricetta, usa:

```bash
cd ../../../Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

Apri `http://localhost:3000` per utilizzare l'interfaccia web di Panacea. I caricamenti dei documenti sono gestiti dal percorso backend `POST /ingest-pdf` con i campi del modulo richiesti `chat_id` e `files[]`.

Esempio di comando di caricamento:

```bash
curl -X POST http://localhost:5000/ingest-pdf \
  -F chat_id=1 \
  -F "files[]=@./path/to/document.pdf"
```

### Guida al caricamento minimale

1. Avvia Panacea dalla radice del repository:

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

2. In un altro terminale, carica un singolo documento di testo o PDF:

```bash
curl -X POST http://localhost:5000/ingest-pdf \
  -F chat_id=1 \
  -F "files[]=@./Cookbook/recipes/03-panacea-document-qa-rag/data/sample-doc.txt"
```

3. Conferma che il backend restituisca una risposta `Document Uploaded` di successo.

4. Usa l'interfaccia web su `http://localhost:3000` e seleziona la stessa sessione di chat per porre domande sul documento caricato.

Se desideri testare l'API direttamente dopo il caricamento, trova l'ID della sessione di chat nell'interfaccia o nel database e invia domande attraverso il flusso di chat dell'app. Panacea recupererà frammenti rilevanti e genererà una risposta fondata.

## Note per il ricettario

Questa ricetta è ideale per un'entrata nel ricettario che spiega come Panacea supporta il lavoro di conoscenza privato. È più concettuale rispetto a uno script di una sola riga, perché il vero valore sta nella comprensione dell'architettura di acquisizione e recupero dei documenti.
