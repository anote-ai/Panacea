# CLI-Konfiguration

Die Anote CLI kann über `.anote.json` im Stammverzeichnis Ihres Projekts oder global über `~/.anote/config.json` konfiguriert werden.

## Konfigurationsdatei

```json
{
  "model": "claude-sonnet-4-6",
  "permissionMode": "default",
  "maxTurns": 20,
  "provider": "anthropic"
}
```

## Verwaltung der Konfiguration

```bash
anote config list          # Alle Einstellungen anzeigen
anote config get model     # Einen Wert abrufen
anote config set model claude-haiku-4-5-20251001  # Einen Wert festlegen
anote config unset model   # Einen Wert entfernen
```
