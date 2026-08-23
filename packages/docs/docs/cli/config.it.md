# Configurazione CLI

Il CLI di Anote può essere configurato tramite `.anote.json` nella radice del tuo progetto o `~/.anote/config.json` globalmente.

## File di Configurazione

```json
{
  "model": "claude-sonnet-4-6",
  "permissionMode": "default",
  "maxTurns": 20,
  "provider": "anthropic"
}
```

## Gestione della Configurazione

```bash
anote config list          # Mostra tutte le impostazioni
anote config get model     # Ottieni un valore
anote config set model claude-haiku-4-5-20251001  # Imposta un valore
anote config unset model   # Rimuovi un valore
```
