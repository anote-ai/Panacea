# Características de la Aplicación Web

## Interfaz de Chat

La vista principal del chat refleja el diseño de ChatGPT: una barra lateral izquierda colapsable con el historial de sesiones y un hilo de mensajes centrado con una barra de entrada en la parte inferior.

## Modo Claro / Oscuro

Alterna con el botón en la parte superior derecha. La preferencia se guarda en `localStorage`.

- **Claro**: fondos blancos/grises claros, texto negro
- **Oscuro**: fondos `#212121`/`#2F2F2F`, texto blanco

## Streaming

La entrada envía una solicitud `POST /api/chat/stream` y lee la respuesta SSE. Un botón de detener aborta la transmisión a mitad de camino.

## Sesiones

Cada conversación es una sesión almacenada en el servidor. Las sesiones se enumeran en la barra lateral y persisten entre cargas de página.
