# Come funziona Panacea

Panacea esegue un **loop agentico**: legge il tuo prompt, decide quali strumenti chiamare, li esegue, legge i risultati e ripete — trasmettendo il suo ragionamento e le modifiche a te — fino a quando il compito è completato o raggiunge un limite di turni.

## Gli strumenti

Per impostazione predefinita, l'agente di Panacea può chiamare:

| Strumento | Scopo |
|---|---|
| `Read` | Leggere un file |
| `Write` | Creare o sovrascrivere un file |
| `Edit` | Apportare una modifica mirata a un file |
| `Bash` | Eseguire un comando della shell |
| `Glob` | Trovare file per pattern |
| `Grep` | Cercare contenuti nei file |

Al alcuni comandi restringono questa lista — `anote review` e `anote diff`, ad esempio, consentono solo `Read`, `Glob`, `Grep` e `Bash`, poiché una revisione non dovrebbe scrivere file.

## Turni e compattazione

Ogni coppia di chiamata/riposta dello strumento conta come un turno. L'agente si ferma dopo `maxTurns` (predefinito 30, configurabile tramite `anote config set maxTurns <n>` o `.anote.json`). Le sessioni lunghe vengono compattate dopo `compactAfterMessages` (predefinito 40) per mantenere la finestra di contesto gestibile.

## Streaming

Ogni superficie — CLI, VS Code, Web, Desktop — comunica con lo stesso endpoint backend (`POST /api/chat/stream`), che trasmette la risposta del modello e l'attività degli strumenti tramite SSE mentre accade. Puoi vedere le letture dei file, le modifiche e l'output dei comandi in tempo reale, non solo la risposta finale.

## Multi-provider

Il loop dell'agente non è legato a un solo modello. `anote ask --compare` esegue lo stesso prompt su più modelli affiancati, e `--model` nella maggior parte dei comandi accetta qualsiasi fornitore configurato (`claude-sonnet-4-6`, `gpt-4.1`, `gemini-2.5-pro`, o un `ollama/<model>` locale).

## Prossimi passi

- [Modalità di autorizzazione](../use-panacea/permission-modes.md) — controlla se l'agente chiede prima di modificare o eseguire comandi
- [Estendi Panacea](extend.md) — CLAW.md e hook
- [Comandi CLI](../cli/commands.md) — il riferimento completo ai comandi
