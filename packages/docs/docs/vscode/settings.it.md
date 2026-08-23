# Impostazioni dell'estensione VS Code

Configura l'estensione nell'interfaccia delle impostazioni di VS Code o in `settings.json`.

| Impostazione | Predefinito | Descrizione |
|--------------|-------------|-------------|
| `anote.model` | `claude-sonnet-4-6` | Modello predefinito da utilizzare |
| `anote.apiKey` | `""` | Chiave API di Anthropic (o usa la variabile d'ambiente) |
| `anote.permissionMode` | `default` | Modalità di autorizzazione dello strumento: `default`, `auto`, `manual` |
| `anote.showToolUse` | `true` | Mostra le chiamate agli strumenti nel pannello chat |

```json
{
  "anote.model": "claude-sonnet-4-6",
  "anote.permissionMode": "default"
}
```
