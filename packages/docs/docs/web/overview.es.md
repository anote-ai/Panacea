# Descripción general de la aplicación web

La aplicación web de Anote AI es una interfaz de chat estilo ChatGPT que se conecta al backend de Anote.

## Características

- Modo claro y oscuro (detecta automáticamente la preferencia del sistema)
- Respuestas en streaming a través de SSE
- Historial de sesiones de chat en una barra lateral colapsable
- Selector de modelo (Claude, GPT-4o, etc.)
- Carga de documentos y preguntas y respuestas
- Diseño responsivo

## Ejecución local

```bash
cd packages/web
npm install
npm run dev
```

La aplicación se ejecuta en `http://localhost:3000` y envía las llamadas API a `http://localhost:5000`.
