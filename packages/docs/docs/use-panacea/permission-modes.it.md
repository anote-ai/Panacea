# Modalità di Permesso

Panacea ha tre modalità di permesso, che controllano se l'agente chiede prima di scrivere file o eseguire comandi.

| Modalità | Comportamento |
|---|---|
| `default` | Conferma prima di modificare file o eseguire comandi non in sola lettura |
| `acceptEdits` | Accetta automaticamente le modifiche ai file senza chiedere |
| `bypassPermissions` | Esegue tutto senza conferma — usare con cautela |

Imposta globalmente o per progetto:

```bash
anote config set permissionMode acceptEdits
```

oppure in `.anote.json`:

```json
{ "permissionMode": "acceptEdits" }
```

## Sovrascritture per comando

La maggior parte dei comandi non richiede di toccare la configurazione globale — prendono i propri flag per la stessa idea:

| Flag | Disponibile su | Effetto |
|---|---|---|
| `--auto` | `fix`, `refactor` | Accetta automaticamente le modifiche solo per questa esecuzione |
| `--dry-run` | `fix`, `docs`, `migrate`, `security`, `perf`, `refactor`, `generate`, `changelog`, `commit`, `review` | Mostra cosa accadrebbe senza scrivere nulla |
| `--no-edit` | `ask` | Sola lettura — l'agente non può modificare i file anche se lo desidera |
| `--yes` | `init` | Salta i prompt interattivi, accetta i valori predefiniti |

`anote fix --loop` implica automaticamente `acceptEdits`, poiché deve continuare a modificare attraverso le iterazioni senza fermarsi a chiedere ogni volta.

## Hook come livello di politica

Per qualsiasi cosa più specifica di "chiedi vs. non chiedere" — come bloccare le chiamate `Bash` che toccano un certo percorso — usa un hook `preToolUse`. Vedi [Estendi Panacea](../core-concepts/extend.md).

## Prossimi passi

- [Come funziona Panacea](../core-concepts/how-it-works.md) — il ciclo dell'agente che questi modi controllano
- [Esplora la directory .anote](../core-concepts/anote-directory.md) — dove vive `permissionMode` nella configurazione
