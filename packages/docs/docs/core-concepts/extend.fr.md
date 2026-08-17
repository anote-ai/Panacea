# Étendre Panacea

Deux façons de personnaliser le comportement de Panacea dans votre projet : **CLAW.md** pour des instructions persistantes, et les **hooks** pour exécuter vos propres commandes autour des appels d'outils.

## CLAW.md — mémoire du projet

`CLAW.md` est un fichier markdown que Panacea lit pour le contexte du projet — la même idée qu'un README, mais destiné à l'agent plutôt qu'à un humain. `anote init` en génère un automatiquement, pré-rempli avec votre stack détectée et les commandes de vérification (test/lint/build) :

```markdown
# CLAW.md

This file provides guidance to Anote AI when working with code in this repository.

## Project overview

<!-- Describe what this project does -->

## Stack

TypeScript · Next.js

## Verification

Run these before considering a change complete:

  npm test
  npm run lint

## Working agreement

- Read relevant files before making changes
- Run the verification commands after modifying logic
- Keep changes small and focused
- Prefer editing existing files over creating new ones
```

Modifiez-le librement — ajoutez des notes d'architecture, des conventions, ou des points sur lesquels l'agent se trompe régulièrement. Panacea le lit au début de chaque session dans ce répertoire.

## Hooks — exécuter vos propres commandes autour des appels d'outils

Les hooks exécutent une commande shell avant (`preToolUse`) ou après (`postToolUse`) chaque appel d'outil, configurés dans `.anote.json` :

```json
{
  "hooks": {
    "preToolUse": ["./scripts/check-tool-policy.sh"],
    "postToolUse": ["npx prettier --write ."]
  }
}
```

**Sémantique des codes de sortie :**

| Code de sortie | Effet |
|---|---|
| `0` | Autoriser — la sortie stdout est capturée comme message informatif |
| `2` | Refuser — la sortie stdout est capturée comme raison, affichée à l'agent |
| autre valeur | Avertir mais autoriser |

Utilisez `preToolUse` pour bloquer les commandes risquées ou appliquer une politique avant leur exécution ; utilisez `postToolUse` pour des choses comme le formatage automatique après chaque modification.

## Prochaines étapes

- [Explorer le répertoire .anote](anote-directory.md) — où vivent CLAW.md et la configuration
- [Modes de permission](../use-panacea/permission-modes.md) — l'autre levier pour contrôler ce que l'agent peut faire
