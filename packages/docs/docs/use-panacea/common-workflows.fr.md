# Flux de travail communs

Modèles étape par étape pour les tâches quotidiennes avec le CLI de Panacea.

## Explorer une base de code inconnue

```bash
anote explain                       # générer une visite CODEBASE.md
anote explain src/auth.ts "comment cela fonctionne-t-il ?"
anote index && anote search "validation JWT"
```

`explain` sans arguments écrit un aperçu `CODEBASE.md` de tout le dépôt. Indiquez-lui un fichier ou posez une question spécifique pour approfondir.

## Corriger un bug

```bash
anote fix --error "TypeError: impossible de lire la propriété 'id' de undefined"
anote fix src/handler.ts "le gestionnaire de webhook perd des événements sous charge"
anote fix --loop --cmd "npm test"          # continuer à itérer jusqu'à ce que les tests passent
```

## Écrire et valider

```bash
anote generate "un middleware de limitation de débit pour Express" -o src/middleware/rateLimit.ts
anote test src/middleware/rateLimit.ts --write
anote commit                                # message de commit généré par l'IA
```

## Réviser avant de pousser

```bash
anote diff --staged                         # réviser les modifications mises en scène
anote review --pr 42                        # ou réviser une PR GitHub ouverte
anote security --severity high              # audit OWASP Top 10
```

## Ouvrir une demande de tirage

```bash
anote pr --gh                               # générer une description, ouvrir avec le CLI gh
```

## Refactoriser en toute sécurité

```bash
anote refactor src/legacy.ts "extraire la logique de validation dans sa propre fonction" --dry-run
anote refactor src/legacy.ts "extraire la logique de validation dans sa propre fonction" --auto
```

Essayez toujours `--dry-run` d'abord sur tout ce que vous n'avez pas encore révisé.

## Continuer à travailler pendant que vous faites autre chose

```bash
anote watch "src/**/*.ts"                   # ré-analyser à chaque sauvegarde
```

## Documenter au fur et à mesure

```bash
anote docs src/api.ts --style jsdoc
anote changelog --since v1.2.0
```

## Prochaines étapes

- [Bibliothèque de prompts](prompt-library.md) — points de départ à copier-coller
- [Commandes CLI](../cli/commands.md) — référence complète des drapeaux
