# Explorer le répertoire .anote

Le CLI de Panacea lit la configuration depuis deux endroits : un fichier par projet et un fichier global.

## Configuration du projet

Panacea recherche en remontant depuis votre répertoire actuel le premier fichier trouvé, dans cet ordre :

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

| Clé | Objectif |
|---|---|
| `model` | Modèle par défaut pour ce projet |
| `permissionMode` | `default`, `acceptEdits`, ou `bypassPermissions` — voir [Modes de permission](../use-panacea/permission-modes.md) |
| `provider` | Remplacement explicite du fournisseur (généralement auto-détecté à partir de `model`) |
| `baseUrl` | URL de base pour les endpoints compatibles OpenAI, par ex. `http://localhost:11434/v1` pour Ollama |
| `maxTurns` | Plafond de tours par session |
| `compactAfterMessages` | Quand compacter l'historique de session |
| `hooks` | Hooks shell `preToolUse` / `postToolUse` — voir [Étendre Panacea](extend.md) |

`anote init` crée `.anote.json` pour vous. `anote config` le lit et l'écrit :

```bash
anote config              # afficher la config effective (globale + locale)
anote config get model
anote config set model gpt-4.1
anote config path         # afficher le chemin du fichier de config global
anote config edit         # ouvrir la config globale dans $EDITOR
```

## Configuration globale

`~/.anote/config.json` contient vos valeurs par défaut — appliquées chaque fois qu'un projet ne les remplace pas. La configuration du projet l'emporte toujours sur la configuration globale.

## CLAW.md

Pas du JSON — un fichier markdown que l'agent lit pour le contexte du projet au début de chaque session. Voir [Étendre Panacea](extend.md) pour savoir ce qu'il contient.

## Prochaines étapes

- [Modes de permission](../use-panacea/permission-modes.md)
- [Gérer les sessions](../use-panacea/sessions.md)
