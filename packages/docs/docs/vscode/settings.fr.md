# Paramètres de l'extension VS Code

Configurez l'extension dans l'interface des paramètres de VS Code ou `settings.json`.

| Paramètre | Par défaut | Description |
|-----------|------------|-------------|
| `anote.model` | `claude-sonnet-4-6` | Modèle par défaut à utiliser |
| `anote.apiKey` | `""` | Clé API d'Anthropic (ou utilisez une variable d'environnement) |
| `anote.permissionMode` | `default` | Mode de permission de l'outil : `default`, `auto`, `manual` |
| `anote.showToolUse` | `true` | Afficher les appels d'outil dans le panneau de chat |

```json
{
  "anote.model": "claude-sonnet-4-6",
  "anote.permissionMode": "default"
}
```
