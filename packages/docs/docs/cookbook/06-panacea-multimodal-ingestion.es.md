# Ingesta de Documentos Multi-Modal de Panacea

Esta receta explica cómo Panacea extiende la pregunta y respuesta sobre documentos + RAG (ver [receta 03](03-panacea-document-qa-rag.md)) más allá del texto plano a imágenes, audio, video y hojas de cálculo, haciendo que todos ellos sean buscables a través del mismo pipeline de fragmentación y embebido.

## Lo que aprenderás

- Cómo Panacea clasifica una carga por tipo MIME y la dirige a un servicio de ingestión dedicado
- Cómo las imágenes y los fotogramas de video se convierten en texto indexable utilizando un LLM capaz de visión
- Cómo el audio (incluida la pista de audio de un video) se transcribe con Whisper
- Cómo las hojas de cálculo se convierten en tablas Markdown en lugar de ser aplastadas en un volcado de texto no buscable
- Las banderas de características y los límites de tamaño que rigen la ingestión multi-modal

## Por qué esto es importante

Tika (el extractor de texto de documentos por defecto) solo puede manejar de manera útil formatos basados en texto. Sin un manejo adicional, una imagen, un clip de audio, un video o una hoja de cálculo cargados fallarían en la ingestión o perderían toda su estructura. Panacea, en cambio, detecta el tipo de medio en el momento de la carga y llama a un servicio diseñado específicamente que produce texto limpio, que luego se almacena como `document_text` y fluye a través del mismo camino de recuperación que cualquier otro documento, por lo que una captura de pantalla, una grabación de llamada o una hoja de cálculo de ventas se vuelven respondibles a través del chat como lo haría un PDF.

## Archivos clave de Panacea

| Archivo | Por qué es importante |
|---|---|
| `Panacea/backend/api_endpoints/documents/handler.py` | Detecta el tipo MIME/extensión en la carga y dirige al servicio de ingestión correcto |
| `Panacea/backend/services/vision_service.py` | `describe_image()` — produce una descripción textual detallada de una imagen utilizando GPT-4o o Claude vision |
| `Panacea/backend/services/audio_service.py` | `transcribe_audio()` — transcribe audio con OpenAI Whisper |
| `Panacea/backend/services/video_service.py` | Extrae fotogramas con `ffmpeg`, describe cada uno con el servicio de visión, transcribe la pista de audio y entrelaza ambos |
| `Panacea/backend/services/tabular_service.py` | `ingest_tabular()` — convierte CSV/TSV/XLSX/XLS/ODS en tablas Markdown que preservan encabezados y filas |
| `Panacea/backend/agents/config.py` | Banderas de características de `AgentConfig`: `ENABLE_MULTIMODAL`, `MAX_IMAGE_BYTES`, `MAX_AUDIO_BYTES`, `MAX_VIDEO_BYTES`, `VIDEO_FRAME_INTERVAL_SECS`, `VIDEO_MAX_FRAMES` |

## Cómo funciona

1. Un archivo se carga a través del mismo endpoint utilizado para documentos regulares; `handler.py` detecta el tipo MIME/extensión para clasificarlo como imagen, video, audio, tabular o texto/documento plano.
2. **Imagen** → `vision_service.describe_image()` envía la imagen (codificada en base64) a un modelo capaz de visión con un aviso que le indica transcribir cualquier texto visible, describir gráficos/diagramas/capturas de pantalla de UI y notar objetos y diseño, por lo que la descripción por sí sola es suficiente para que la búsqueda semántica la encuentre más tarde.
3. **Audio** → `audio_service.transcribe_audio()` llama a Whisper (`whisper-1`) y devuelve una transcripción con metadatos de duración/idioma.
4. **Video** → `video_service` extrae fotogramas a intervalos fijos (`VIDEO_FRAME_INTERVAL_SECS`, por defecto 30s, limitado a `VIDEO_MAX_FRAMES`) utilizando `ffmpeg`, describe cada fotograma con el servicio de visión, transcribe la pista de audio por separado y entrelaza ambos en un documento con marcas de tiempo.
5. **Tabular** → `tabular_service.ingest_tabular()` analiza cada hoja de forma nativa (a través de `csv`/`pandas`+`openpyxl`/`xlrd`) y la renderiza como una tabla Markdown, retrocediendo a CSV plano para filas más allá de las primeras 500 para que nada se pierda del índice de búsqueda, incluso si no se renderiza bien.
6. Cualquier texto que salga de cualquiera de estos servicios se almacena como `document_text` y se fragmenta/embebe exactamente como un documento normal, por lo que es recuperable a través del flujo estándar de Q&A RAG de la receta 03.

Cada servicio está diseñado para **nunca fallar**: una llamada de visión fallida, una dependencia faltante o un archivo demasiado grande devuelve una cadena de marcador de posición (por ejemplo, `"[Imagen demasiado grande para análisis en línea (23.4 MB). Límite: 20 MB.]"`) para que el registro del documento siempre se cree en lugar de fallar toda la carga.

## Ejecútalo localmente

Desde la raíz del espacio de trabajo (`anote/panacea`):

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

La ingestión multi-modal está activada por defecto (`ENABLE_MULTIMODAL=true`). Establece estos en `backend/.env` para ajustar el comportamiento:

```bash
ENABLE_MULTIMODAL=true        # interruptor maestro
MAX_IMAGE_BYTES=20971520      # 20 MB por defecto
MAX_AUDIO_BYTES=26214400      # 25 MB por defecto
MAX_VIDEO_BYTES=524288000     # 500 MB por defecto
VIDEO_FRAME_INTERVAL_SECS=30
VIDEO_MAX_FRAMES=20
```

La ingestión de video requiere además que `ffmpeg` esté presente en el `PATH` del contenedor backend (ya incluido en la imagen de Docker proporcionada). La ingestión de Excel requiere `openpyxl` (XLSX/ODS) y `xlrd` (XLS legado), y ambos servicios de visión/audio necesitan que se establezcan `OPENAI_API_KEY` y/o `ANTHROPIC_API_KEY` dependiendo de `DEFAULT_AGENT_MODEL_TYPE`.

### Pruébalo

```bash
curl -X POST http://localhost:5000/ingest-pdf \
  -F chat_id=1 \
  -F "files[]=@./screenshot.png"

curl -X POST http://localhost:5000/ingest-pdf \
  -F chat_id=1 \
  -F "files[]=@./quarterly_sales.xlsx"
```

Luego, en la interfaz web en `http://localhost:3000`, abre la misma sesión de chat y haz una pregunta sobre la imagen o la hoja de cálculo que acabas de cargar; Panacea responde a partir de la descripción generada/tablas Markdown exactamente como lo haría con un PDF.

## Notas para el libro de recetas

Esta receta se complementa bien con la receta 03: es el mismo pipeline RAG, solo que con un embudo más amplio de formatos de entrada. Vale la pena señalar a los lectores que la "calidad del índice" para imágenes/video es solo tan buena como la descripción del modelo de visión, por lo que la sintonización de avisos en `_INDEXING_PROMPT` de `vision_service.py` es un punto de personalización natural.
