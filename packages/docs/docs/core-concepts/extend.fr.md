# Étendre Panacea

Deux façons de personnaliser le comportement de Panacea dans votre projet : **CLAW.md** pour des instructions persistantes, et **hooks** pour exécuter vos propres commandes autour des appels d'outils.

## CLAW.md — mémoire du projet

`CLAW.md` est un fichier markdown que Panacea lit pour le contexte du projet — la même idée qu'un README destiné à l'agent plutôt qu'à un humain. `anote init` en génère un automatiquement, pré-rempli avec votre pile détectée et les commandes de vérification (test/lint/build) :

```markdown
# CLAW.md

Ce fichier fournit des conseils à Anote AI lors du travail avec le code dans ce dépôt.

## Aperçu du projet

<!-- Décrivez ce que fait ce projet -->

## Pile

TypeScript · Next.js

## Vérification

Exécutez ces commandes avant de considérer un changement comme complet :

  npm test
  npm run lint

## Accord de travail

- Lisez les fichiers pertinents avant de faire des modifications
- Exécutez les commandes de vérification après avoir modifié la logique
- Gardez les changements petits et ciblés
- Préférez modifier les fichiers existants plutôt que d'en créer de nouveaux
```

Modifiez-le librement — ajoutez des notes d'architecture, des conventions ou des choses que l'agent continue de mal faire. Panacea le lit au début de chaque session dans ce répertoire.

## Hooks — exécutez vos propres commandes autour des appels d'outils

Les hooks exécutent une commande shell avant (`preToolUse`) ou après (`postToolUse`) chaque appel d'outil, configurés dans `.anote.json` :

```json
{
  "hooks": {
    "preToolUse": ["./scripts/check-tool-policy.sh"],
    "postToolUse": ["npx prettier --write ."]
  }
}
```

**Sémantique du code de sortie :**

| Code de sortie | Effet |
|---|---|
| `0` | Autoriser — stdout est capturé comme un message d'information |
| `2` | Refuser — stdout est capturé comme la raison, affichée à l'agent |
| tout autre | Avertir mais autoriser |

Utilisez `preToolUse` pour bloquer des commandes risquées ou appliquer des politiques avant qu'elles ne s'exécutent ; utilisez `postToolUse` pour des choses comme le formatage automatique après chaque modification.

## Prochaines étapes

- [Explorer le répertoire .anote](anote-directory.md) — où se trouvent CLAW.md et la configuration
- [Modes de permission](../use-panacea/permission-modes.md) — le levier supplémentaire sur ce que l'agent peut faire
