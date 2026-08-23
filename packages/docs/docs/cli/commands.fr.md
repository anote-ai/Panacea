# Commandes CLI

## `anote ask`

Posez n'importe quelle question sur votre code.

```bash
anote ask "comment fonctionne le middleware d'authentification ?"
anote ask --file src/auth.ts "expliquez ce fichier"
anote ask --compare  # côte à côte sur plusieurs modèles
cat file.py | anote ask "trouver des bugs"
```

## `anote fix`

Corrigez les bugs dans le répertoire actuel.

```bash
anote fix
anote fix --loop                    # itérer jusqu'à ce que les tests passent
anote fix --max-iterations 5        # limiter les itérations
anote fix --file src/broken.ts      # corriger un fichier spécifique
```

## `anote review`

Examinez le code pour détecter des bugs, des problèmes de sécurité et de qualité.

```bash
anote review                        # examiner le répertoire actuel
anote review --file src/handler.ts  # examiner un fichier spécifique
anote review --pr 42                # publier une révision AI sur GitHub PR
```

## `anote index`

Construisez un index de recherche sémantique TF-IDF de votre code.

```bash
anote index              # indexer le répertoire actuel
anote index --watch      # surveiller les changements et réindexer
anote index /path/to/dir # indexer un répertoire spécifique
```

## `anote search`

Recherchez sémantiquement dans votre code indexé.

```bash
anote search "validation de jeton JWT"
anote search "connexion à la base de données" --top 10
anote search "middleware d'auth" --json
```

## `anote doctor`

Vérifiez votre environnement pour des problèmes de configuration.

```bash
anote doctor
```

Vérifications : Node.js ≥ 18, `ANTHROPIC_API_KEY` défini, `.anote.json` présent, `CLAW.md` présent, git installé.

## `anote changelog`

Générez une entrée CHANGELOG.md à partir de l'historique git.

```bash
anote changelog
anote changelog --since v1.2.0
anote changelog --dry-run
```

## `anote docs`

Générez de la documentation pour le code non documenté.

```bash
anote docs
anote docs src/api.ts
anote docs --style jsdoc
anote docs --dry-run
```

## `anote migrate`

Migration de code assistée par IA.

```bash
anote migrate --from "React 17" --to "React 18"
anote migrate --from "axios" --to "fetch"
anote migrate --dry-run
```

## `anote security`

Audit de sécurité de votre code (OWASP Top 10).

```bash
anote security
anote security --severity high
anote security --fix
```

## `anote perf`

Analyse de performance.

```bash
anote perf
anote perf --focus "database,bundle"
anote perf --fix
```
