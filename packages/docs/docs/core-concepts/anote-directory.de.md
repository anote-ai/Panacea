# Erkunde das .anote Verzeichnis

Die CLI von Panacea liest die Konfiguration aus zwei Quellen: einer projektbezogenen Datei und einer globalen.

## Projektkonfiguration

Panacea sucht von deinem aktuellen Verzeichnis aus nach der ersten Datei, die es in dieser Reihenfolge findet:

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

| Schlüssel | Zweck |
|---|---|
| `model` | Standardmodell für dieses Projekt |
| `permissionMode` | `default`, `acceptEdits` oder `bypassPermissions` — siehe [Berechtigungsmodi](../use-panacea/permission-modes.md) |
| `provider` | Explizite Anbieterüberschreibung (normalerweise automatisch von `model` erkannt) |
| `baseUrl` | Basis-URL für OpenAI-kompatible Endpunkte, z.B. `http://localhost:11434/v1` für Ollama |
| `maxTurns` | Maximalanzahl an Zügen pro Sitzung |
| `compactAfterMessages` | Wann die Sitzungsverlauf kompakt gemacht werden soll |
| `hooks` | `preToolUse` / `postToolUse` Shell-Hooks — siehe [Panacea erweitern](extend.md) |

`anote init` erstellt `.anote.json` für dich. `anote config` liest und schreibt es:

```bash
anote config              # zeigt die effektive Konfiguration (global + lokal)
anote config get model
anote config set model gpt-4.1
anote config path         # gibt den Pfad zur globalen Konfigurationsdatei aus
anote config edit         # öffnet die globale Konfiguration in $EDITOR
```

## Globale Konfiguration

`~/.anote/config.json` enthält deine Standardwerte — die angewendet werden, wenn ein Projekt diese nicht überschreibt. Die Projektkonfiguration hat immer Vorrang vor der globalen Konfiguration.

## CLAW.md

Kein JSON — eine Markdown-Datei, die der Agent zu Beginn jeder Sitzung für den Projektkontext liest. Siehe [Panacea erweitern](extend.md) für den Inhalt.

## Nächste Schritte

- [Berechtigungsmodi](../use-panacea/permission-modes.md)
- [Sitzungen verwalten](../use-panacea/sessions.md)
