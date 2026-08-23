# Puerta de enlace API compatible con OpenAI de Panacea

Esta receta explica cómo apuntar cualquier herramienta construida contra el SDK de OpenAI a Panacea en su lugar — sin cambios en el código — mientras se sigue teniendo acceso a extensiones RAG específicas de Panacea como fuentes de documentos fundamentadas.

## Lo que aprenderás

- Cómo `AnoteOpenAI` refleja la interfaz del cliente real `openai.OpenAI`
- Cómo subir documentos y obtener respuestas fundamentadas en documentos a través de una API con forma de chat-completions
- Cómo funciona el streaming a través de Eventos Enviados por el Servidor (SSE), al estilo de OpenAI
- Dónde aparecen las extensiones específicas de Panacea (`anote_sources`, `anote_message_id`) en la respuesta

## Por qué es importante

Una gran cantidad de herramientas existentes — integraciones de LangChain, scripts internos, marcos de agentes de terceros — está escrita contra la forma del SDK de OpenAI (`client.chat.completions.create(...)`, `client.models.list()`). En lugar de pedir a cada integrador que aprenda un SDK personalizado de Panacea, Panacea envía un cliente que se integra fácilmente y que habla la misma interfaz, para que los equipos puedan adoptar el backend privado y fundamentado en documentos de Panacea sin reescribir su código de integración.

## Archivos clave de Panacea

| Archivo | Por qué es importante |
|---|---|
| `Panacea/backend/sdk/anoteai/openai_compat.py` | Cliente `AnoteOpenAI`: `CompletionsClient`, `ModelsClient`, `DocumentsClient` y el analizador de flujo SSE |
| `Panacea/backend/sdk/anoteai/core.py` | La clase SDK subyacente `PrivateChatbot` que envuelve la capa de compatibilidad |
| `Panacea/backend/sdk/anoteai/handlers/private_handlers.py` | Manejo de solicitudes compartido con el SDK nativo |
| Rutas del servidor: `POST /v1/chat/completions`, `GET /v1/models`, `POST /v1/question-answer`, `POST /public/upload` | Los endpoints con forma de OpenAI (y uno específico de Panacea) que llama el cliente |

## Cómo funciona

1. Instancia el cliente exactamente como el SDK de OpenAI, pero apuntando a tu backend de Panacea:

   ```python
   from anoteai.openai_compat import AnoteOpenAI

   client = AnoteOpenAI(
       api_key="tu-clave-api-anote",       # o establece ANOTE_API_KEY
       base_url="http://localhost:5000",    # o https://api.anote.ai
   )
   ```

2. Para preguntas y respuestas fundamentadas en documentos, primero sube archivos — `client.documents.upload(...)` publica datos de formulario multipart en `/public/upload` y devuelve un `chat_id`.
3. Haz una pregunta de la misma manera que llamarías al SDK de OpenAI, pasando el `chat_id` a través de `extra_body` para que el servidor sepa qué documentos recuperar:

   ```python
   upload_resp = client.documents.upload("ruta/al/informe.pdf")
   chat_id = upload_resp["chat_id"]

   response = client.chat.completions.create(
       model="gpt-4o",
       messages=[{"role": "user", "content": "Resume los hallazgos clave."}],
       extra_body={"chat_id": chat_id},
   )
   print(response.choices[0].message.content)
   print("Fuentes:", response.anote_sources)
   ```

4. La respuesta se mapea en dataclasses que reflejan el verdadero SDK de OpenAI (`ChatCompletion`, `Choice`, `Message`, `Usage`), además de dos extensiones de Panacea: `anote_message_id` y `anote_sources` (los fragmentos/citas recuperados que respaldan la respuesta).
5. Pasa `stream=True` para obtener un generador de objetos `ChatCompletionChunk` analizados a partir de líneas SSE de `text/event-stream` (`data: {...}` por token, terminado por `data: [DONE]`) — la misma forma que produce el cliente de streaming de OpenAI.
6. `client.models.list()` llama a `GET /v1/models` para el descubrimiento de modelos, devolviendo objetos `Model`/`ModelList` igual que el SDK de OpenAI.

## Ejecútalo localmente

Desde la raíz del espacio de trabajo (`anote/panacea`):

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

Instala la única dependencia del cliente y establece tu clave API:

```bash
pip install requests
export ANOTE_API_KEY=tu_clave_api_aqui   # macOS/Linux
set ANOTE_API_KEY=tu_clave_api_aqui      # Windows cmd
```

### Recorrido mínimo

```python
from anoteai.openai_compat import AnoteOpenAI

client = AnoteOpenAI(base_url="http://localhost:5000")

# Chat simple, sin documentos:
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "¿Cuál es la capital de Francia?"}],
)
print(response.choices[0].message.content)

# Streaming:
for chunk in client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Cuenta hasta cinco."}],
    stream=True,
):
    for choice in chunk.choices:
        if choice.delta.content:
            print(choice.delta.content, end="", flush=True)
```

## Notas para el libro de recetas

Esta receta es un buen complemento a la receta 03 — es la misma capacidad de preguntas y respuestas/RAG fundamentadas en documentos, pero expuesta a través de una interfaz que las herramientas existentes basadas en el SDK de OpenAI pueden consumir sin modificaciones. Vale la pena señalar a los lectores que `DocumentsClient.upload()`/`question_answer()` son ayudantes específicos de Panacea que se superponen al núcleo compatible con OpenAI, no son parte de la especificación de OpenAI en sí.
