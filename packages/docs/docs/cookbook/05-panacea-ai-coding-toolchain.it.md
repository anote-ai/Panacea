# Panacea AI Coding Toolchain

Questa ricetta spiega come l'esperienza di codifica AI di Panacea viene fornita attraverso CLI, SDK e VS Code.

## Cosa imparerai

- I diversi punti di accesso alla codifica AI in Panacea
- Come la CLI, l'SDK e l'estensione di VS Code si relazionano con il backend condiviso
- Le principali capacità del prodotto per assistenza al codice privato
- Dove cercare nel repository i dettagli di implementazione

## Perché è importante

Panacea è costruito come un prodotto unificato con più interfacce:

- una **CLI** che alimenta `anote chat`, ricerca di codice e revisione del repository
- un **estensione di VS Code** per assistenza AI in-editor
- un **SDK** per incorporare Panacea in altre applicazioni

Queste interfacce condividono un backend e un livello di ragionamento guidato da agenti, il che rende il prodotto coerente tra desktop, web e flussi di lavoro di codice.

## File chiave di Panacea

| File | Perché è importante |
|---|---|
| `Panacea/packages/cli` | Implementazione CLI in TypeScript per flussi di lavoro degli sviluppatori |
| `Panacea/packages/vscode` | Estensione di VS Code e integrazione chat |
| `Panacea/packages/sdk` | SDK in TypeScript per accesso programmatico |
| `Panacea/packages/backend` | Servizio backend condiviso che alimenta tutte le interazioni UI e CLI |

## Come funziona

- Un'azione di codifica dell'utente inizia dalla CLI, dall'SDK o dall'estensione di VS Code.
- La richiesta viene inviata all'API backend di Panacea.
- Il backend utilizza l'orchestrazione degli agenti e i fornitori di modelli per produrre risposte consapevoli del codice.
- La risposta viene restituita nella stessa interfaccia, con suggerimenti di codice, spiegazioni o correzioni.

## Funzionalità utili del prodotto

- **CLI**: `anote chat`, ricerca di repository, revisione del codice, generazione di codice e assistenza potenziata da embeddings.
- **VS Code**: chat inline, anteprime delle differenze, azioni di codice e risposte in streaming.
- **SDK**: un wrapper client per l'API di Panacea, che consente integrazioni personalizzate.

## Esegui localmente

Dalla radice del workspace (`anote/panacea`):

```bash
cd Panacea
cp packages/backend/.env.example packages/backend/.env
docker compose up --build
```

Questo avvia i servizi backend e frontend condivisi.

In un altro terminale, esegui il pacchetto CLI:

```bash
cd Panacea/packages/cli
npm install
npm run dev
```

Poi puoi utilizzare la CLI localmente o compilarla con `npm run build`.

Per lo sviluppo di VS Code, apri `Panacea/packages/vscode` in VS Code e avvia l'estensione con il debugger.

## Note per il ricettario

Questa ricetta è utile per i membri del team che necessitano di una panoramica ad alto livello del prodotto di codifica AI multi-interfaccia di Panacea. Può anche indirizzare i lettori verso i file di implementazione che possono modificare o estendere.
