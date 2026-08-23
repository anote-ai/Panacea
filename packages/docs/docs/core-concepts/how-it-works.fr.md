# Comment fonctionne Panacea

Panacea exécute une **boucle agentique** : il lit votre invite, décide quels outils appeler, les exécute, lit les résultats et répète — en diffusant son raisonnement et ses modifications vers vous — jusqu'à ce que la tâche soit terminée ou qu'il atteigne une limite de tours.

## Les outils

Par défaut, l'agent de Panacea peut appeler :

| Outil | But |
|---|---|
| `Read` | Lire un fichier |
| `Write` | Créer ou écraser un fichier |
| `Edit` | Apporter un changement ciblé à un fichier |
| `Bash` | Exécuter une commande shell |
| `Glob` | Trouver des fichiers par motif |
| `Grep` | Rechercher dans le contenu des fichiers |

Certaines commandes restreignent cette liste — `anote review` et `anote diff`, par exemple, n'autorisent que `Read`, `Glob`, `Grep` et `Bash`, car une révision ne devrait pas écrire de fichiers.

## Tours et compactage

Chaque paire appel/réponse d'outil compte comme un tour. L'agent s'arrête après `maxTurns` (par défaut 30, configurable via `anote config set maxTurns <n>` ou `.anote.json`). Les longues sessions sont compactées après `compactAfterMessages` (par défaut 40) pour garder la fenêtre de contexte gérable.

## Diffusion

Chaque surface — CLI, VS Code, Web, Bureau — communique avec le même point de terminaison backend (`POST /api/chat/stream`), qui diffuse la réponse du modèle et l'activité des outils via SSE au fur et à mesure. Vous voyez les lectures de fichiers, les modifications et la sortie des commandes en direct, pas seulement la réponse finale.

## Multi-fournisseur

La boucle de l'agent n'est pas liée à un seul modèle. `anote ask --compare` exécute la même invite sur plusieurs modèles côte à côte, et `--model` sur la plupart des commandes accepte tout fournisseur configuré (`claude-sonnet-4-6`, `gpt-4.1`, `gemini-2.5-pro`, ou un `ollama/<model>` local).

## Prochaines étapes

- [Modes de permission](../use-panacea/permission-modes.md) — contrôler si l'agent demande avant de modifier ou d'exécuter des commandes
- [Étendre Panacea](extend.md) — CLAW.md et hooks
- [Commandes CLI](../cli/commands.md) — la référence complète des commandes
