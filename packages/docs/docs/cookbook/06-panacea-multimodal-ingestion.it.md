# Panacea Multi-Modal Document Ingestion

Questa ricetta spiega come Panacea estende il Q&A dei documenti + RAG (vedi [ricetta 03](03-panacea-document-qa-rag.md)) oltre il testo semplice a immagini, audio, video e fogli di calcolo — rendendoli tutti ricercabili attraverso lo stesso pipeline di chunking e embedding.

## Cosa imparerai

- Come Panacea classifica un upload per tipo MIME e lo instrada a un servizio di ingestione dedicato
- Come le immagini e i fotogrammi video vengono trasformati in testo indicizzabile utilizzando un LLM capace di visione
- Come l'audio (inclusa la traccia audio di un video) viene trascritto con Whisper
- Come i fogli di calcolo vengono convertiti in tabelle Markdown invece di essere appiattiti in un dump di testo non ricercabile
- Le feature flags e i limiti di dimensione che governano l'ingestione multi-modale

## Perché è importante

Tika (l'estrattore di testo dei documenti predefinito) può gestire utilmente solo formati basati su testo. Senza un'ulteriore gestione, un'immagine, un clip audio, un video o un foglio di calcolo caricato fallirebbero nell'ingestione o perderebbero tutta la loro struttura. Panacea invece rileva il tipo di media al momento del caricamento e chiama un servizio appositamente costruito che produce testo pulito, che viene poi memorizzato come `document_text` e fluisce attraverso lo stesso percorso di recupero di qualsiasi altro documento — quindi uno screenshot, una registrazione di chiamata o un foglio di calcolo di vendita diventano tutti interrogabili tramite chat come un PDF.

## File chiave di Panacea

| File | Perché è importante |
|---|---|
| `Panacea/backend/api_endpoints/documents/handler.py` | Rileva il tipo MIME/estensione al caricamento e instrada al giusto servizio di ingestione |
| `Panacea/backend/services/vision_service.py` | `describe_image()` — produce una descrizione testuale dettagliata di un'immagine utilizzando GPT-4o o Claude vision |
| `Panacea/backend/services/audio_service.py` | `transcribe_audio()` — trascrive l'audio con OpenAI Whisper |
| `Panacea/backend/services/video_service.py` | Estrae fotogrammi con `ffmpeg`, descrive ciascuno con il servizio di visione, trascrive la traccia audio e interleava entrambi |
| `Panacea/backend/services/tabular_service.py` | `ingest_tabular()` — converte CSV/TSV/XLSX/XLS/ODS in tabelle Markdown che preservano intestazioni e righe |
| `Panacea/backend/agents/config.py` | Flag delle funzionalità `AgentConfig`: `ENABLE_MULTIMODAL`, `MAX_IMAGE_BYTES`, `MAX_AUDIO_BYTES`, `MAX_VIDEO_BYTES`, `VIDEO_FRAME_INTERVAL_SECS`, `VIDEO_MAX_FRAMES` |

## Come funziona

1. Un file viene caricato attraverso lo stesso endpoint utilizzato per i documenti regolari; `handler.py` rileva il tipo MIME/estensione per classificarlo come immagine, video, audio, tabulare o testo semplice/documento.
2. **Immagine** → `vision_service.describe_image()` invia l'immagine (codificata in base64) a un modello capace di visione con un prompt che istruisce a trascrivere qualsiasi testo visibile, descrivere grafici/diagrammi/screenshot dell'interfaccia utente e notare oggetti e layout — quindi la descrizione da sola è sufficiente affinché la ricerca semantica la trovi in seguito.
3. **Audio** → `audio_service.transcribe_audio()` chiama Whisper (`whisper-1`) e restituisce una trascrizione con metadati di durata/language.
4. **Video** → `video_service` estrae fotogrammi a un intervallo fisso (`VIDEO_FRAME_INTERVAL_SECS`, predefinito 30s, limitato a `VIDEO_MAX_FRAMES`) utilizzando `ffmpeg`, descrive ciascun fotogramma con il servizio di visione, trascrive la traccia audio separatamente e interleava entrambi in un documento timestampato.
5. **Tabulare** → `tabular_service.ingest_tabular()` analizza ciascun foglio nativamente (tramite `csv`/`pandas`+`openpyxl`/`xlrd`) e lo rende come una tabella Markdown, tornando a CSV semplice per righe oltre le prime 500 in modo che nulla venga perso dall'indice di ricerca anche se non è reso in modo gradevole.
6. Qualsiasi testo prodotto da uno di questi servizi viene memorizzato come `document_text` e chunked/embedded esattamente come un documento normale, quindi è recuperabile attraverso il flusso standard RAG Q&A dalla ricetta 03.

Ogni servizio è progettato per **non sollevare mai** — una chiamata di visione fallita, una dipendenza mancante o un file di dimensioni eccessive restituisce una stringa segnaposto (ad es. `"[Immagine troppo grande per l'analisi inline (23.4 MB). Limite: 20 MB.]"`) in modo che il record del documento venga sempre creato invece di far fallire l'intero caricamento.

## Esegui localmente

Dalla radice del workspace (`anote/panacea`):

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

L'ingestione multi-modale è attivata per impostazione predefinita (`ENABLE_MULTIMODAL=true`). Imposta questi in `backend/.env` per regolare il comportamento:

```bash
ENABLE_MULTIMODAL=true        # interruttore principale
MAX_IMAGE_BYTES=20971520      # predefinito 20 MB
MAX_AUDIO_BYTES=26214400      # predefinito 25 MB
MAX_VIDEO_BYTES=524288000     # predefinito 500 MB
VIDEO_FRAME_INTERVAL_SECS=30
VIDEO_MAX_FRAMES=20
```

L'ingestione video richiede inoltre che `ffmpeg` sia presente nel `PATH` del container backend (già incluso nell'immagine Docker fornita). L'ingestione di Excel richiede `openpyxl` (XLSX/ODS) e `xlrd` (XLS legacy), e entrambi i servizi di visione/audio necessitano di `OPENAI_API_KEY` e/o `ANTHROPIC_API_KEY` impostati a seconda di `DEFAULT_AGENT_MODEL_TYPE`.

### Provalo

```bash
curl -X POST http://localhost:5000/ingest-pdf \
  -F chat_id=1 \
  -F "files[]=@./screenshot.png"

curl -X POST http://localhost:5000/ingest-pdf \
  -F chat_id=1 \
  -F "files[]=@./quarterly_sales.xlsx"
```

Poi, nell'interfaccia web a `http://localhost:3000`, apri la stessa sessione di chat e fai una domanda sull'immagine o sul foglio di calcolo che hai appena caricato — Panacea risponde dalla descrizione generata/tabella Markdown esattamente come farebbe da un PDF.

## Note per il ricettario

Questa ricetta si abbina bene con la ricetta 03: è lo stesso pipeline RAG, solo con un imbuto più ampio di formati di input. Vale la pena far notare ai lettori che la "qualità dell'indice" per immagini/video è solo buona quanto la descrizione del modello di visione, quindi la regolazione del prompt in `_INDEXING_PROMPT` di `vision_service.py` è un punto di personalizzazione naturale.
