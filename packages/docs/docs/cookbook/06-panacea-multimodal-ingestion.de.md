# Panacea Multi-Modal Dokumentenaufnahme

Dieses Rezept erklärt, wie Panacea die Dokumenten-Q&A + RAG (siehe [Rezept 03](03-panacea-document-qa-rag.md)) über reinen Text hinaus auf Bilder, Audio, Video und Tabellenkalkulationen erweitert – wodurch all diese durch dasselbe Chunking- und Embedding-Pipeline durchsuchbar werden.

## Was Sie lernen werden

- Wie Panacea einen Upload nach MIME-Typ klassifiziert und an einen dedizierten Aufnahme-Service weiterleitet
- Wie Bilder und Video-Frames in indexierbaren Text umgewandelt werden, indem ein vision-fähiges LLM verwendet wird
- Wie Audio (einschließlich des Audiotracks eines Videos) mit Whisper transkribiert wird
- Wie Tabellenkalkulationen in Markdown-Tabellen umgewandelt werden, anstatt in einen nicht durchsuchbaren Textdump flattenisiert zu werden
- Die Feature-Flags und Größenlimits, die die multi-modale Aufnahme steuern

## Warum das wichtig ist

Tika (der Standard-Dokumenten-Text-Extractor) kann nur nützlich mit textbasierten Formaten umgehen. Ohne zusätzliche Verarbeitung würde ein hochgeladenes Bild, ein Audio-Clip, ein Video oder eine Tabelle entweder nicht aufgenommen werden oder seine gesamte Struktur verlieren. Panacea erkennt stattdessen den Medientyp zum Zeitpunkt des Uploads und ruft einen speziell entwickelten Service auf, der sauberen Text erzeugt, der dann als `document_text` gespeichert wird und denselben Abrufpfad wie jedes andere Dokument durchläuft – sodass ein Screenshot, eine Anrufaufzeichnung oder eine Verkaufs-Tabelle alle über den Chat beantwortet werden können, wie es bei einer PDF der Fall wäre.

## Wichtige Panacea-Dateien

| Datei | Warum es wichtig ist |
|---|---|
| `Panacea/backend/api_endpoints/documents/handler.py` | Erkennt MIME-Typ/Erweiterung beim Upload und leitet an den richtigen Aufnahme-Service weiter |
| `Panacea/backend/services/vision_service.py` | `describe_image()` — erzeugt eine detaillierte Textbeschreibung eines Bildes mit GPT-4o oder Claude Vision |
| `Panacea/backend/services/audio_service.py` | `transcribe_audio()` — transkribiert Audio mit OpenAI Whisper |
| `Panacea/backend/services/video_service.py` | Extrahiert Frames mit `ffmpeg`, beschreibt jeden mit dem Vision-Service, transkribiert den Audiotrack und interleaved beides |
| `Panacea/backend/services/tabular_service.py` | `ingest_tabular()` — konvertiert CSV/TSV/XLSX/XLS/ODS in Markdown-Tabellen, die Header und Zeilen beibehalten |
| `Panacea/backend/agents/config.py` | `AgentConfig` Feature-Flags: `ENABLE_MULTIMODAL`, `MAX_IMAGE_BYTES`, `MAX_AUDIO_BYTES`, `MAX_VIDEO_BYTES`, `VIDEO_FRAME_INTERVAL_SECS`, `VIDEO_MAX_FRAMES` |

## Wie es funktioniert

1. Eine Datei wird über denselben Endpunkt hochgeladen, der für reguläre Dokumente verwendet wird; `handler.py` erkennt den MIME-Typ/Erweiterung, um sie als Bild, Video, Audio, tabellarisch oder reinen Text/Dokument zu klassifizieren.
2. **Bild** → `vision_service.describe_image()` sendet das Bild (base64-kodiert) an ein vision-fähiges Modell mit einem Prompt, der es anweist, sichtbaren Text zu transkribieren, Diagramme/Diagramme/UI-Screenshots zu beschreiben und Objekte und Layout zu notieren – sodass die Beschreibung allein ausreicht, damit die semantische Suche es später findet.
3. **Audio** → `audio_service.transcribe_audio()` ruft Whisper (`whisper-1`) auf und gibt ein Transkript mit Dauer-/Sprachmetadaten zurück.
4. **Video** → `video_service` extrahiert Frames in einem festen Intervall (`VIDEO_FRAME_INTERVAL_SECS`, standardmäßig 30s, begrenzt auf `VIDEO_MAX_FRAMES`) mit `ffmpeg`, beschreibt jeden Frame mit dem Vision-Service, transkribiert den Audiotrack separat und interleaved beides in ein zeitgestempeltes Dokument.
5. **Tabellarisch** → `tabular_service.ingest_tabular()` analysiert jedes Blatt nativ (über `csv`/`pandas`+`openpyxl`/`xlrd`) und rendert es als Markdown-Tabelle, wobei es auf einfaches CSV für Zeilen über die ersten 500 zurückfällt, sodass nichts aus dem Suchindex verloren geht, selbst wenn es nicht schön gerendert wird.
6. Jeder Text, der aus einem dieser Dienste kommt, wird als `document_text` gespeichert und genau wie ein normales Dokument chunked/embedded, sodass er über den standardmäßigen RAG Q&A-Fluss aus Rezept 03 abrufbar ist.

Jeder Service ist so konzipiert, dass er **niemals fehlschlägt** – ein fehlgeschlagener Vision-Aufruf, eine fehlende Abhängigkeit oder eine übergroße Datei gibt einen Platzhalter-String zurück (z.B. `"[Bild zu groß für die Inline-Analyse (23,4 MB). Limit: 20 MB.]"`), sodass der Dokumentenposten immer erstellt wird, anstatt den gesamten Upload fehlschlagen zu lassen.

## Lokal ausführen

Vom Arbeitsbereichs-Stammverzeichnis (`anote/panacea`):

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

Die multi-modale Aufnahme ist standardmäßig aktiviert (`ENABLE_MULTIMODAL=true`). Setzen Sie diese in `backend/.env`, um das Verhalten anzupassen:

```bash
ENABLE_MULTIMODAL=true        # Hauptschalter
MAX_IMAGE_BYTES=20971520      # 20 MB Standard
MAX_AUDIO_BYTES=26214400      # 25 MB Standard
MAX_VIDEO_BYTES=524288000     # 500 MB Standard
VIDEO_FRAME_INTERVAL_SECS=30
VIDEO_MAX_FRAMES=20
```

Die Videoaufnahme erfordert zusätzlich, dass `ffmpeg` im `PATH` des Backend-Containers vorhanden ist (bereits im bereitgestellten Docker-Image enthalten). Die Excel-Aufnahme erfordert `openpyxl` (XLSX/ODS) und `xlrd` (legacy XLS), und beide Vision-/Audio-Services benötigen `OPENAI_API_KEY` und/oder `ANTHROPIC_API_KEY`, je nach `DEFAULT_AGENT_MODEL_TYPE`.

### Probieren Sie es aus

```bash
curl -X POST http://localhost:5000/ingest-pdf \
  -F chat_id=1 \
  -F "files[]=@./screenshot.png"

curl -X POST http://localhost:5000/ingest-pdf \
  -F chat_id=1 \
  -F "files[]=@./quarterly_sales.xlsx"
```

Öffnen Sie dann im Web-UI unter `http://localhost:3000` dieselbe Chatsitzung und stellen Sie eine Frage zu dem Bild oder der Tabelle, die Sie gerade hochgeladen haben – Panacea antwortet aus der generierten Beschreibung/Markdown-Tabelle genau so, wie es bei einer PDF der Fall wäre.

## Hinweise für das Kochbuch

Dieses Rezept passt gut zu Rezept 03: es ist dasselbe RAG-Pipeline, nur mit einem breiteren Trichter von Eingabeformaten. Es ist erwähnenswert, dass die "Indexqualität" für Bilder/Videos nur so gut ist wie die Beschreibung des Vision-Modells, sodass die Anpassung des Prompts in `vision_service.py`'s `_INDEXING_PROMPT` ein natürlicher Anpassungspunkt ist.
