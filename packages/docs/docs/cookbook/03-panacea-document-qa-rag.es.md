# Preguntas y Respuestas de Documentos de Panacea + RAG

Esta receta explica cómo Panacea construye preguntas y respuestas de documentos privados con generación aumentada por recuperación (RAG).

## Lo que aprenderás

- Cómo Panacea ingiere documentos y los almacena como texto buscable
- Cómo el backend recupera fragmentos relevantes para una pregunta
- Cómo el sistema utiliza incrustaciones y fuentes de documentos para fundamentar respuestas
- Cómo se captura la retroalimentación de preguntas y respuestas y mejora las respuestas futuras

## Por qué es importante

Panacea está diseñado para permitir que los equipos hagan preguntas sobre documentos privados sin enviarlos a un servicio de chat de terceros. El flujo de trabajo es:

1. Subir documentos
2. Fragmentar e incrustar contenido
3. Recuperar fragmentos relevantes para una consulta de usuario
4. Responder utilizando un LLM con citas
5. Capturar retroalimentación para mejorar la calidad

## Archivos clave de Panacea

| Archivo | Por qué es importante |
|---|---|
| `Panacea/backend/api_endpoints/documents/handler.py` | Rutas de API para la carga e ingestión de documentos |
| `Panacea/backend/database/db.py` | Lógica SQL para el almacenamiento y recuperación de documentos |
| `Panacea/backend/database/qa_feedback.py` | Captura de retroalimentación para preguntas y respuestas de documentos |
| `Panacea/backend/agents/multi_agent_system.py` | Agentes de recuperación de documentos utilizados en flujos de trabajo de múltiples agentes |

## Cómo funciona

- Los documentos se suben a través del backend y se almacenan en `documents.document_text`.
- El sistema fragmenta documentos grandes y crea metadatos de recuperación para una búsqueda rápida.
- Cuando un usuario hace una pregunta, Panacea selecciona uno o más agentes especializados para recuperar los mejores fragmentos y luego genera una respuesta.
- El resultado incluye citas de fuentes para que los usuarios puedan rastrear la respuesta hasta el documento original.
- Las señales de retroalimentación se registran en `qa_feedback` para permitir mejoras futuras en la calidad.

## Ejecútalo localmente

Desde la raíz del espacio de trabajo (`anote/panacea`):

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

Esto inicia el backend, la aplicación web, MySQL, Redis y Tika.

Si ya estás dentro de la carpeta de la receta, usa:

```bash
cd ../../../Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

Abre `http://localhost:3000` para usar la interfaz web de Panacea. Las cargas de documentos son manejadas por la ruta del backend `POST /ingest-pdf` con los campos de formulario requeridos `chat_id` y `files[]`.

Ejemplo de comando de carga:

```bash
curl -X POST http://localhost:5000/ingest-pdf \
  -F chat_id=1 \
  -F "files[]=@./path/to/document.pdf"
```

### Guía mínima de carga

1. Inicia Panacea desde la raíz del repositorio:

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

2. En otra terminal, sube un solo documento de texto o PDF:

```bash
curl -X POST http://localhost:5000/ingest-pdf \
  -F chat_id=1 \
  -F "files[]=@./Cookbook/recipes/03-panacea-document-qa-rag/data/sample-doc.txt"
```

3. Confirma que el backend devuelve una respuesta exitosa de `Documento Cargado`.

4. Usa la interfaz web en `http://localhost:3000` y selecciona la misma sesión de chat para hacer preguntas sobre el documento cargado.

Si deseas probar la API directamente después de la carga, encuentra el ID de la sesión de chat en la interfaz o en la base de datos y envía preguntas a través del flujo de chat de la aplicación. Panacea recuperará fragmentos relevantes y generará una respuesta fundamentada.

## Notas para el libro de cocina

Esta receta es ideal para una entrada en el libro de cocina que explica cómo Panacea apoya el trabajo de conocimiento privado. Es más conceptual que un script de una línea, porque el verdadero valor radica en entender la arquitectura de ingestión y recuperación de documentos.
