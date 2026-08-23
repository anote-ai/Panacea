# Bibliothèque de Prompts

Copiez-collez des prompts pour `anote ask`, `anote chat`, et `anote fix`, organisés par tâche.

## Comprendre le code

```bash
anote ask "que fait cette base de code, à un niveau élevé ?"
anote ask --file src/payments/webhook.ts "explique-moi ce fichier ligne par ligne"
anote ask "où le limiteur de taux est-il configuré, et quels sont les limites ?"
anote ask "qu'est-ce qui casserait si je supprimais la couche de mise en cache ici ?"
```

## Débogage

```bash
anote fix --error "$(cat error.log)"
anote ask "pourquoi ce test échoue-t-il de manière intermittente mais pas de façon constante ?"
anote fix src/db/pool.ts "les connexions ne sont pas libérées vers le pool"
```

## Revue de code

```bash
anote review --file src/auth/session.ts
anote review --pr 42
anote diff --staged -c "concentrez-vous sur la gestion des erreurs et les cas limites"
```

## Refactorisation

```bash
anote refactor src/utils.ts "divisez ceci en fonctions plus petites et à objectif unique" --dry-run
anote ask "y a-t-il un moyen plus simple d'exprimer cette logique ?" --file src/parser.ts
anote migrate --from "moment" --to "date-fns"
```

## Écriture de tests

```bash
anote test src/utils/validate.ts --coverage --write
anote ask "quels cas limites me manquent pour cette fonction ?" --file src/utils/validate.ts
```

## Sécurité et performance

```bash
anote security --severity high
anote perf --focus "base de données, taille du bundle"
```

## Documentation

```bash
anote docs src/api/client.ts --style jsdoc
anote changelog --since v1.2.0
anote explain --stdout                       # résumé rapide de l'architecture
```

## Prochaines étapes

- [Flux de travail communs](common-workflows.md)
- [Commandes CLI](../cli/commands.md)
