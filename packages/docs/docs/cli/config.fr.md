# Configuration CLI

Le CLI Anote peut être configuré via `.anote.json` dans la racine de votre projet ou `~/.anote/config.json` globalement.

## Fichier de configuration

```json
{
  "model": "claude-sonnet-4-6",
  "permissionMode": "default",
  "maxTurns": 20,
  "provider": "anthropic"
}
```

## Gestion de la configuration

```bash
anote config list          # Afficher tous les paramètres
anote config get model     # Obtenir une valeur
anote config set model claude-haiku-4-5-20251001  # Définir une valeur
anote config unset model   # Supprimer une valeur
```
