# Panacea OpenAI-kompatibles API-Gateway

Dieses Rezept erklärt, wie man jedes Tool, das gegen das OpenAI SDK entwickelt wurde, stattdessen auf Panacea ausrichtet — ohne Änderungen am Code — und dennoch Zugriff auf Panacea-spezifische RAG-Erweiterungen wie fundierte Dokumentenquellen erhält.

## Was Sie lernen werden

- Wie `AnoteOpenAI` die Schnittstelle des echten `openai.OpenAI`-Clients spiegelt
- Wie man Dokumente hochlädt und dokumentenfundierte Antworten über eine API im Format von Chat-Vervollständigungen erhält
- Wie Streaming über Server-Sent Events (SSE) funktioniert, im OpenAI-Stil
- Wo die Panacea-spezifischen Erweiterungen (`anote_sources`, `anote_message_id`) in der Antwort erscheinen

## Warum das wichtig ist

Eine große Menge bestehender Tools — LangChain-Integrationen, interne Skripte, Frameworks von Drittanbietern — ist gegen die Struktur des OpenAI SDKs geschrieben (`client.chat.completions.create(...)`, `client.models.list()`). Anstatt jeden Integrator zu bitten, ein maßgeschneidertes Panacea SDK zu lernen, bietet Panacea einen Drop-in-Client an, der dieselbe Schnittstelle spricht, sodass Teams Panaceas privaten, dokumentenfundierten Backend ohne Neuschreibung ihres Integrationscodes übernehmen können.

## Wichtige Panacea-Dateien

| Datei | Warum es wichtig ist |
|---|---|
| `Panacea/backend/sdk/anoteai/openai_compat.py` | `AnoteOpenAI`-Client: `CompletionsClient`, `ModelsClient`, `DocumentsClient` und der SSE-Stream-Parser |
| `Panacea/backend/sdk/anoteai/core.py` | Die zugrunde liegende `PrivateChatbot` SDK-Klasse, die die Kompatibilitätsschicht umschließt |
| `Panacea/backend/sdk/anoteai/handlers/private_handlers.py` | Anfrageverarbeitung, die mit dem nativen SDK geteilt wird |
| Server-Routen: `POST /v1/chat/completions`, `GET /v1/models`, `POST /v1/question-answer`, `POST /public/upload` | Die OpenAI-ähnlichen (und eine Panacea-spezifische) Endpunkte, die der Client aufruft |

## Wie es funktioniert

1. Instanziieren Sie den Client genau wie das OpenAI SDK, aber auf Ihr Panacea-Backend ausgerichtet:

   ```python
   from anoteai.openai_compat import AnoteOpenAI

   client = AnoteOpenAI(
       api_key="your-anote-api-key",       # oder ANOTE_API_KEY setzen
       base_url="http://localhost:5000",    # oder https://api.anote.ai
   )
   ```

2. Für dokumentenfundierte Q&A laden Sie zuerst Dateien hoch — `client.documents.upload(...)` sendet multipart Formulardaten an `/public/upload` und gibt eine `chat_id` zurück.
3. Stellen Sie eine Frage auf die gleiche Weise, wie Sie das OpenAI SDK aufrufen würden, und übergeben Sie die `chat_id` über `extra_body`, damit der Server weiß, welche Dokumente abgerufen werden sollen:

   ```python
   upload_resp = client.documents.upload("path/to/report.pdf")
   chat_id = upload_resp["chat_id"]

   response = client.chat.completions.create(
       model="gpt-4o",
       messages=[{"role": "user", "content": "Fassen Sie die wichtigsten Ergebnisse zusammen."}],
       extra_body={"chat_id": chat_id},
   )
   print(response.choices[0].message.content)
   print("Quellen:", response.anote_sources)
   ```

4. Die Antwort wird in Datenklassen abgebildet, die das echte OpenAI SDK spiegeln (`ChatCompletion`, `Choice`, `Message`, `Usage`), plus zwei Panacea-Erweiterungen: `anote_message_id` und `anote_sources` (die abgerufenen Abschnitte/Zitationen, die die Antwort unterstützen).
5. Übergeben Sie `stream=True`, um einen Generator von `ChatCompletionChunk`-Objekten zu erhalten, die aus `text/event-stream` SSE-Zeilen geparst werden (`data: {...}` pro Token, beendet mit `data: [DONE]`) — dieselbe Struktur, die der Streaming-Client von OpenAI produziert.
6. `client.models.list()` ruft `GET /v1/models` für die Modellerkennung auf und gibt `Model`/`ModelList`-Objekte zurück, genau wie das OpenAI SDK.

## Lokal ausführen

Vom Arbeitsbereichsroot (`anote/panacea`):

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

Installieren Sie die einzige Abhängigkeit des Clients und setzen Sie Ihren API-Schlüssel:

```bash
pip install requests
export ANOTE_API_KEY=your_api_key_here   # macOS/Linux
set ANOTE_API_KEY=your_api_key_here      # Windows cmd
```

### Minimaler Überblick

```python
from anoteai.openai_compat import AnoteOpenAI

client = AnoteOpenAI(base_url="http://localhost:5000")

# Einfacher Chat, keine Dokumente:
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Was ist die Hauptstadt von Frankreich?"}],
)
print(response.choices[0].message.content)

# Streaming:
for chunk in client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Zähle bis fünf."}],
    stream=True,
):
    for choice in chunk.choices:
        if choice.delta.content:
            print(choice.delta.content, end="", flush=True)
```

## Hinweise für das Kochbuch

Dieses Rezept ist eine gute Ergänzung zu Rezept 03 — es bietet dieselbe Dokumenten-Q&A/RAG-Funktionalität, wird jedoch über eine Schnittstelle bereitgestellt, die bestehende OpenAI-SDK-basierte Tools unverändert konsumieren können. Es ist erwähnenswert, dass `DocumentsClient.upload()`/`question_answer()` Panacea-spezifische Helfer sind, die auf dem OpenAI-kompatiblen Kern aufbauen, und nicht Teil der OpenAI-Spezifikation selbst.
