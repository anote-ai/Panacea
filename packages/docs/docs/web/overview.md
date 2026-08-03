# Web App Overview

The Anote AI web app is a ChatGPT-style chat interface that connects to the Anote backend.

## Features

- Light and dark mode (auto-detects system preference)
- Streaming responses via SSE
- Chat session history in a collapsible sidebar
- Model selector (Claude, GPT-4o, etc.)
- Document upload and Q&A
- Responsive design

## Using the app

1. Go to `/register` and create an account with email/password, or sign in with Google — either lands you on `/login` afterward if you're not already authenticated
2. Once signed in you land on `/app`, the chat view
3. Type a message and send it — the response streams in token-by-token; use the stop button to cancel mid-stream
4. Attach a file from the chat composer to ask questions about a document — it's indexed and shows up under `/documents` too, where you can organize uploads into folders by dragging them
5. Start a new conversation any time — past sessions stay listed in the left sidebar and reload at `/app/chat/:id`
6. Toggle light/dark mode from the theme button — your preference is saved in `localStorage`

## Running Locally

```bash
cd packages/web
npm install
npm run dev
```

The app runs at `http://localhost:3000` and proxies API calls to `http://localhost:5000`.
