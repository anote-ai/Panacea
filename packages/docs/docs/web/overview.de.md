# Web App Übersicht

Die Anote AI Web-App ist eine ChatGPT-ähnliche Chat-Oberfläche, die mit dem Anote-Backend verbunden ist.

## Funktionen

- Hell- und Dunkelmodus (erkennt automatisch die Systemeinstellung)
- Streaming-Antworten über SSE
- Chat-Sitzungshistorie in einer zusammenklappbaren Seitenleiste
- Modellauswahl (Claude, GPT-4o usw.)
- Dokumenten-Upload und Q&A
- Responsives Design

## Lokal Ausführen

```bash
cd packages/web
npm install
npm run dev
```

Die App läuft unter `http://localhost:3000` und leitet API-Aufrufe an `http://localhost:5000` weiter.
