# Explorer le répertoire .anote

Le CLI de Panacea lit la configuration à partir de deux endroits : un fichier par projet et un fichier global.

## Configuration du projet

Panacea recherche vers le haut à partir de votre répertoire actuel pour le premier fichier qu'il trouve, dans cet ordre :

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

| Clé | But |
|---|---|
| `model` | Modèle par défaut pour ce projet |
| `permissionMode` | `default`, `acceptEdits`, ou `bypassPermissions` — voir [Modes de permission](../use-panacea/permission-modes.md) |
| `provider` | Remplacement explicite du fournisseur (généralement détecté automatiquement à partir de `model`) |
| `baseUrl` | URL de base pour les points de terminaison compatibles OpenAI, par exemple `http://localhost:11434/v1` pour Ollama |
| `maxTurns` | Limite de tours par session |
| `compactAfterMessages` | Quand compacter l'historique de la session |
| `hooks` | Hooks shell `preToolUse` / `postToolUse` — voir [Étendre Panacea](extend.md) |

`anote init` crée `.anote.json` pour vous. `anote config` le lit et l'écrit :

```bash
anote config              # afficher la configuration effective (globale + locale)
anote config get model
anote config set model gpt-4.1
anote config path         # imprimer le chemin du fichier de configuration global
anote config edit         # ouvrir la configuration globale dans $EDITOR
```

## Configuration globale

`~/.anote/config.json` contient vos valeurs par défaut — appliquées chaque fois qu'un projet ne les remplace pas. La configuration du projet l'emporte toujours sur la configuration globale.

## CLAW.md

Pas du JSON — un fichier markdown que l'agent lit pour le contexte du projet au début de chaque session. Voir [Étendre Panacea](extend.md) pour ce qui y va.

## Prochaines étapes

- [Modes de permission](../use-panacea/permission-modes.md)
- [Gérer les sessions](../use-panacea/sessions.md)
