# Come funziona Panacea

Panacea esegue un **ciclo agentico**: legge il tuo prompt, decide quali strumenti chiamare, li esegue, legge i risultati e ripete — trasmettendoti in streaming il suo ragionamento e le modifiche — finché il task non è completato o non raggiunge un limite di turni.

## Gli strumenti

Per impostazione predefinita, l'agente di Panacea può chiamare:

| Strumento | Scopo |
|---|---|
| `Read` | Leggere un file |
| `Write` | Creare o sovrascrivere un file |
| `Edit` | Apportare una modifica mirata a un file |
| `Bash` | Eseguire un comando shell |
| `Glob` | Trovare file per pattern |
| `Grep` | Cercare nel contenuto dei file |

Alcuni comandi restringono questo elenco — `anote review` e `anote diff`, ad esempio, consentono solo `Read`, `Glob`, `Grep` e `Bash`, poiché una revisione non dovrebbe scrivere file.

## Turni e compattazione

Ogni coppia chiamata strumento/risposta conta come un turno. L'agente si ferma dopo `maxTurns` (30 di default, configurabile tramite `anote config set maxTurns <n>` o `.anote.json`). Le sessioni lunghe vengono compattate dopo `compactAfterMessages` (40 di default) per mantenere gestibile la finestra di contesto.

## Streaming

Ogni superficie — CLI, VS Code, Web, Desktop — comunica con lo stesso endpoint backend (`POST /api/chat/stream`), che trasmette in streaming la risposta del modello e l'attività degli strumenti via SSE man mano che avviene. Vedi le letture dei file, le modifiche e l'output dei comandi in tempo reale, non solo la risposta finale.

## Multi-provider

Il ciclo dell'agente non è legato a un solo modello. `anote ask --compare` esegue lo stesso prompt su più modelli affiancati, e `--model` sulla maggior parte dei comandi accetta qualsiasi provider configurato (`claude-sonnet-4-6`, `gpt-4.1`, `gemini-2.5-pro`, o un `ollama/<model>` locale).

## Prossimi passi

- [Modalità di permesso](../use-panacea/permission-modes.md) — controlla se l'agente chiede prima di modificare file o eseguire comandi
- [Estendere Panacea](extend.md) — CLAW.md e hooks
- [Comandi CLI](../cli/commands.md) — la referenza completa dei comandi
