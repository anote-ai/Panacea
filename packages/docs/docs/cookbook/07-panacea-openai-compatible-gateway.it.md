# Panacea API Gateway Compatibile con OpenAI

Questa ricetta spiega come puntare qualsiasi strumento costruito contro l'SDK di OpenAI a Panacea invece — senza modifiche al codice — pur ottenendo accesso a estensioni RAG specifiche di Panacea come fonti di documenti ancorate.

## Cosa imparerai

- Come `AnoteOpenAI` rispecchia l'interfaccia del vero client `openai.OpenAI`
- Come caricare documenti e ottenere risposte ancorate ai documenti tramite un'API a forma di completamenti chat
- Come funziona lo streaming tramite Eventi Inviati dal Server (SSE), in stile OpenAI
- Dove compaiono le estensioni specifiche di Panacea (`anote_sources`, `anote_message_id`) nella risposta

## Perché è importante

Una grande quantità di strumenti esistenti — integrazioni LangChain, script interni, framework di agenti di terze parti — è scritta contro la forma dell'SDK di OpenAI (`client.chat.completions.create(...)`, `client.models.list()`). Piuttosto che chiedere a ogni integratore di apprendere un SDK Panacea su misura, Panacea fornisce un client drop-in che parla la stessa interfaccia, in modo che i team possano adottare il backend privato e ancorato ai documenti di Panacea senza riscrivere il loro codice di integrazione.

## File chiave di Panacea

| File | Perché è importante |
|---|---|
| `Panacea/backend/sdk/anoteai/openai_compat.py` | Client `AnoteOpenAI`: `CompletionsClient`, `ModelsClient`, `DocumentsClient` e il parser del flusso SSE |
| `Panacea/backend/sdk/anoteai/core.py` | La classe SDK sottostante `PrivateChatbot` che il layer di compatibilità avvolge |
| `Panacea/backend/sdk/anoteai/handlers/private_handlers.py` | Gestione delle richieste condivisa con l'SDK nativo |
| Rotte del server: `POST /v1/chat/completions`, `GET /v1/models`, `POST /v1/question-answer`, `POST /public/upload` | Gli endpoint a forma di OpenAI (e uno specifico di Panacea) che il client chiama |

## Come funziona

1. Instanzia il client esattamente come l'SDK di OpenAI, ma puntato al tuo backend di Panacea:

   ```python
   from anoteai.openai_compat import AnoteOpenAI

   client = AnoteOpenAI(
       api_key="your-anote-api-key",       # oppure imposta ANOTE_API_KEY
       base_url="http://localhost:5000",    # oppure https://api.anote.ai
   )
   ```

2. Per domande e risposte ancorate ai documenti, carica prima i file — `client.documents.upload(...)` invia dati di modulo multipart a `/public/upload` e restituisce un `chat_id`.
3. Fai una domanda nello stesso modo in cui chiameresti l'SDK di OpenAI, passando il `chat_id` attraverso `extra_body` affinché il server sappia quali documenti recuperare:

   ```python
   upload_resp = client.documents.upload("path/to/report.pdf")
   chat_id = upload_resp["chat_id"]

   response = client.chat.completions.create(
       model="gpt-4o",
       messages=[{"role": "user", "content": "Riassumi i risultati chiave."}],
       extra_body={"chat_id": chat_id},
   )
   print(response.choices[0].message.content)
   print("Fonti:", response.anote_sources)
   ```

4. La risposta è mappata in dataclass che rispecchiano il vero SDK di OpenAI (`ChatCompletion`, `Choice`, `Message`, `Usage`), più due estensioni di Panacea: `anote_message_id` e `anote_sources` (i frammenti/citazioni recuperati che supportano la risposta).
5. Passa `stream=True` per ottenere un generatore di oggetti `ChatCompletionChunk` analizzati dalle righe SSE `text/event-stream` (`data: {...}` per token, terminato da `data: [DONE]`) — la stessa forma prodotta dal client di streaming di OpenAI.
6. `client.models.list()` chiama `GET /v1/models` per la scoperta dei modelli, restituendo oggetti `Model`/`ModelList` proprio come l'SDK di OpenAI.

## Esegui localmente

Dalla radice del workspace (`anote/panacea`):

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

Installa l'unica dipendenza del client e imposta la tua chiave API:

```bash
pip install requests
export ANOTE_API_KEY=your_api_key_here   # macOS/Linux
set ANOTE_API_KEY=your_api_key_here      # Windows cmd
```

### Passaggio minimo

```python
from anoteai.openai_compat import AnoteOpenAI

client = AnoteOpenAI(base_url="http://localhost:5000")

# Chat semplice, senza documenti:
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Qual è la capitale della Francia?"}],
)
print(response.choices[0].message.content)

# Streaming:
for chunk in client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Conta fino a cinque."}],
    stream=True,
):
    for choice in chunk.choices:
        if choice.delta.content:
            print(choice.delta.content, end="", flush=True)
```

## Note per il ricettario

Questa ricetta è un buon complemento alla ricetta 03 — ha la stessa capacità di Q&A/RAG sui documenti, ma esposta attraverso un'interfaccia che gli strumenti esistenti basati sull'SDK di OpenAI possono consumare senza modifiche. Vale la pena segnalare ai lettori che `DocumentsClient.upload()`/`question_answer()` sono helper specifici di Panacea sovrapposti al core compatibile con OpenAI, non parte della specifica di OpenAI stessa.
