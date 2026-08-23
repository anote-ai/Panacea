# Esplora la directory .anote

Il CLI di Panacea legge la configurazione da due luoghi: un file per progetto e uno globale.

## Configurazione del progetto

Panacea cerca verso l'alto dalla tua directory corrente per il primo file che trova, in questo ordine:

- `.anote.json`
- `.claw.json`
- `anote.config.json`

```json
{
  "model": "claude-sonnet-4-6",
  "permissionMode": "default",
  "maxTurns": 20,
  "compactAfterMessages": 40,
  "hooks": {
    "preToolUse": [],
    "postToolUse": []
  }
}
```

| Chiave | Scopo |
|---|---|
| `model` | Modello predefinito per questo progetto |
| `permissionMode` | `default`, `acceptEdits`, o `bypassPermissions` — vedi [Modalità di permesso](../use-panacea/permission-modes.md) |
| `provider` | Sovrascrittura esplicita del provider (di solito rilevato automaticamente da `model`) |
| `baseUrl` | URL di base per gli endpoint compatibili con OpenAI, ad esempio `http://localhost:11434/v1` per Ollama |
| `maxTurns` | Limite di turni per sessione |
| `compactAfterMessages` | Quando compattare la cronologia della sessione |
| `hooks` | Hook shell `preToolUse` / `postToolUse` — vedi [Estendi Panacea](extend.md) |

`anote init` crea `.anote.json` per te. `anote config` lo legge e lo scrive:

```bash
anote config              # mostra la configurazione effettiva (globale + locale)
anote config get model
anote config set model gpt-4.1
anote config path         # stampa il percorso del file di configurazione globale
anote config edit         # apre la configurazione globale in $EDITOR
```

## Configurazione globale

`~/.anote/config.json` contiene le tue impostazioni predefinite — applicate ogni volta che un progetto non le sovrascrive. La configurazione del progetto ha sempre la precedenza sulla configurazione globale.

## CLAW.md

Non JSON — un file markdown che l'agente legge per il contesto del progetto all'inizio di ogni sessione. Vedi [Estendi Panacea](extend.md) per cosa inserire.

## Prossimi passi

- [Modalità di permesso](../use-panacea/permission-modes.md)
- [Gestisci sessioni](../use-panacea/sessions.md)
