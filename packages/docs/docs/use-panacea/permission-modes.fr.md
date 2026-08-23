# Modes de Permission

Panacea a trois modes de permission, contrôlant si l'agent demande avant d'écrire des fichiers ou d'exécuter des commandes.

| Mode | Comportement |
|---|---|
| `default` | Confirme avant de modifier des fichiers ou d'exécuter des commandes non en lecture seule |
| `acceptEdits` | Accepte automatiquement les modifications de fichiers sans demander |
| `bypassPermissions` | Exécute tout sans confirmation — à utiliser avec précaution |

Définissez-le globalement ou par projet :

```bash
anote config set permissionMode acceptEdits
```

ou dans `.anote.json` :

```json
{ "permissionMode": "acceptEdits" }
```

## Remplacements par commande

La plupart des commandes ne nécessitent pas que vous touchiez à la configuration globale — elles prennent leurs propres drapeaux pour la même idée :

| Drapeau | Disponible sur | Effet |
|---|---|---|
| `--auto` | `fix`, `refactor` | Accepte automatiquement les modifications pour cette exécution uniquement |
| `--dry-run` | `fix`, `docs`, `migrate`, `security`, `perf`, `refactor`, `generate`, `changelog`, `commit`, `review` | Montre ce qui se passerait sans écrire quoi que ce soit |
| `--no-edit` | `ask` | Lecture seule — l'agent ne peut pas modifier les fichiers même s'il le souhaite |
| `--yes` | `init` | Ignore les invites interactives, accepte les valeurs par défaut |

`anote fix --loop` implique automatiquement `acceptEdits`, car il doit continuer à modifier à travers les itérations sans s'arrêter pour demander à chaque fois.

## Hooks comme couche de politique

Pour tout ce qui est plus spécifique que "demander vs. ne pas demander" — comme bloquer les appels `Bash` qui touchent un certain chemin — utilisez un hook `preToolUse` à la place. Voir [Étendre Panacea](../core-concepts/extend.md).

## Prochaines étapes

- [Comment Panacea fonctionne](../core-concepts/how-it-works.md) — la boucle de l'agent que ces modes contrôlent
- [Explorer le répertoire .anote](../core-concepts/anote-directory.md) — où `permissionMode` se trouve dans la configuration
