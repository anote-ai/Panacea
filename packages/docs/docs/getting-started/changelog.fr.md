# Journal des modifications

Panacea ne publie pas encore de fichier de journal des modifications maintenu à la main — la source de vérité pour ce qui a été expédié est :

- **[Versions GitHub](https://github.com/anote-ai/Panacea/releases)** — versions taguées pour le CLI, l'extension VS Code et d'autres packages
- **[Historique des commits](https://github.com/anote-ai/Panacea/commits/main)** — chaque changement, dans l'ordre

## Générer un pour votre propre projet

Le CLI peut écrire un journal des modifications à partir de l'historique git pour *votre* code source :

```bash
anote changelog                    # depuis le dernier tag
anote changelog --since v1.2.0
anote changelog --dry-run          # imprimer au lieu d'écrire CHANGELOG.md
```

Cela écrit dans le propre `CHANGELOG.md` de votre projet, pas celui de Panacea.
