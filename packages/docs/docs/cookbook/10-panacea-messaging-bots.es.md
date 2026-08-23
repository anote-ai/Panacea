# Bots de Mensajería Multicanal de Panacea

Esta receta explica las integraciones de estilo chat-ops de Panacea: bots independientes de Slack, SMS y WhatsApp que permiten a los usuarios hacer preguntas de codificación desde las aplicaciones de mensajería que ya utilizan.

## Lo que aprenderás

- El patrón de diseño compartido entre los tres bots: recibir → llamar a un LLM → recortar al límite de caracteres del canal → responder
- Cómo el bot de Slack maneja los hilos y edita un marcador de posición "pensando…" en su lugar
- Cómo los bots de SMS/WhatsApp responden de manera sincrónica utilizando Twilio's TwiML
- Una brecha arquitectónica actual que vale la pena conocer antes de extender estos bots

## Por qué esto es importante

No todos los usuarios quieren abrir una interfaz web o un IDE para hacer una pregunta: las integraciones de estilo chat-ops se encuentran con las personas donde ya están. Cada bot es un pequeño servicio Flask independiente, por lo que un equipo puede ejecutar solo los canales que necesita (por ejemplo, solo Slack) sin tener que poner en marcha el resto de la pila de Panacea.

## Archivos clave de Panacea

| Archivo | Por qué es importante |
|---|---|
| `Panacea/packages/bots/slack/app.py` | Aplicación Slack Bolt; soporta Modo Socket o webhook HTTP; marcador de posición "pensando…" actualizado en su lugar |
| `Panacea/packages/bots/sms/app.py` | Manejador de webhook de SMS de Twilio (`MessagingResponse`/TwiML) |
| `Panacea/packages/bots/whatsapp/app.py` | Manejador de webhook de sandbox de WhatsApp de Twilio |
| `Panacea/packages/bots/{slack,sms,whatsapp}/.env.example` | Credenciales requeridas por canal |

## Cómo funciona

1. **Slack** (`slack/app.py`): escucha eventos `app_mention`. `extract_query()` elimina la mención `<@BOT_ID>` del texto del mensaje. Publica inmediatamente un mensaje de marcador de posición `_Anote está pensando…_`, luego ejecuta la llamada al LLM en un hilo en segundo plano y edita ese marcador de posición en su lugar a través de `client.chat_update(...)` o, si la publicación del marcador de posición falla, envía una nueva respuesta en hilo.
2. **SMS** (`sms/app.py`): Twilio envía cada texto entrante a `/sms` como datos de formulario (`Body`, `From`). El manejador llama al LLM de manera sincrónica y devuelve un `MessagingResponse` (TwiML) con la respuesta — Twilio lo entrega como un texto de seguimiento.
3. **WhatsApp** (`whatsapp/app.py`): mismo patrón de TwiML que SMS, conectado al webhook de sandbox de WhatsApp de Twilio en lugar de a un número de teléfono.
4. Los tres llaman a la **API de Anthropic directamente** (`anthropic.Anthropic(...).messages.create(...)`) con un aviso del sistema compartido que describe a Anote como un asistente de codificación — actualmente no pasan por el backend de Panacea, por lo que no obtienen RAG/grounding de documentos, medición de créditos, ni orquestación multi-agente de las recetas 03/04/08.
5. Las respuestas se recortan al límite de cada canal antes de enviarlas: Slack 2900 caracteres, SMS/WhatsApp 1600 caracteres, cada una con un aviso de truncamiento añadido si se corta.

### Brecha arquitectónica a conocer

Debido a que estos bots llaman a Anthropic directamente en lugar de enrutar a través del backend de Panacea, un usuario de Slack/SMS/WhatsApp no puede actualmente hacer preguntas basadas en documentos que han subido a Panacea, y su uso no se mide a través del sistema de créditos en la receta 08. Si deseas paridad de canal con la interfaz web, el siguiente paso natural es intercambiar la llamada directa `anthropic_client.messages.create(...)` por una solicitud al propio `/v1/chat/completions` de Panacea (la puerta de enlace compatible con OpenAI de la receta 07) para que estos bots hereden RAG, orquestación y facturación de forma gratuita.

## Ejecútalo localmente

Cada bot es independiente: instala y ejecuta solo los que necesites.

### Slack

```bash
cd Panacea/packages/bots/slack
pip install -r requirements.txt
cp .env.example .env   # completa SLACK_BOT_TOKEN, SLACK_SIGNING_SECRET, ANTHROPIC_API_KEY
python app.py
```

Establece `SLACK_APP_TOKEN` en `.env` para ejecutar en Modo Socket (no se necesita URL pública); de lo contrario, sirve HTTP en `PORT` (por defecto 3000) y espera que el webhook de la API de Eventos de Slack apunte a `POST /slack/events`.

### SMS

```bash
cd Panacea/packages/bots/sms
pip install -r requirements.txt
cp .env.example .env   # completa ANTHROPIC_API_KEY
python app.py
```

Configura el webhook de SMS de tu número de teléfono de Twilio a `POST https://<your-host>/sms` (puerto por defecto 3001).

### WhatsApp

```bash
cd Panacea/packages/bots/whatsapp
pip install -r requirements.txt
cp .env.example .env   # completa ANTHROPIC_API_KEY
python app.py
```

Configura el webhook de sandbox de WhatsApp de Twilio para apuntar a `POST /whatsapp` en este servicio.

Cada bot también expone `GET /health` para una rápida verificación de disponibilidad.

## Notas para el libro de recetas

Esta es una buena receta para "extender Panacea": los lectores pueden ver la versión directa a Anthropic funcionando en minutos, y luego seguir la nota de brecha arquitectónica anterior para conectarlo a través del backend de Panacea en su lugar para respuestas fundamentadas y medidas.
