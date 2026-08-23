# Panoramica dell'App Web

L'app web di Anote AI è un'interfaccia di chat in stile ChatGPT che si connette al backend di Anote.

## Caratteristiche

- Modalità chiara e scura (rileva automaticamente la preferenza di sistema)
- Risposte in streaming tramite SSE
- Cronologia delle sessioni di chat in una barra laterale espandibile
- Selettore di modelli (Claude, GPT-4o, ecc.)
- Caricamento di documenti e Q&A
- Design reattivo

## Esecuzione Locale

```bash
cd packages/web
npm install
npm run dev
```

L'app è in esecuzione su `http://localhost:3000` e inoltra le chiamate API a `http://localhost:5000`.
