# VS Code Erweiterungseinstellungen

Konfigurieren Sie die Erweiterung in der VS Code-Einstellungsbenutzeroberfläche oder in `settings.json`.

| Einstellung | Standard | Beschreibung |
|-------------|----------|--------------|
| `anote.model` | `claude-sonnet-4-6` | Standardmodell, das verwendet werden soll |
| `anote.apiKey` | `""` | Anthropic API-Schlüssel (oder verwenden Sie die Umgebungsvariable) |
| `anote.permissionMode` | `default` | Berechtigungsmodus des Tools: `default`, `auto`, `manual` |
| `anote.showToolUse` | `true` | Zeige Toolaufrufe im Chat-Panel an |

```json
{
  "anote.model": "claude-sonnet-4-6",
  "anote.permissionMode": "default"
}
```
