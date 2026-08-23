# Gérer les sessions

Chaque conversation `anote chat` est enregistrée localement en tant que session — ses messages, l'utilisation des jetons et le répertoire de travail.

## Lister les sessions

```bash
anote sessions list
anote sessions ls --limit 50
```

```
Sessions enregistrées (3) :
  a1b2c3d4  12 msgs  in=4,200 out=1,800  il y a 10m  /Users/you/project
  e5f6a7b8  4 msgs   in=900 out=400      il y a 2h   /Users/you/other-project
```

## Afficher une session

```bash
anote sessions show a1b2c3d4
anote sessions show a1b2c3d4 --limit 50   # plus d'historique de messages
```

Affiche la conversation, les totaux de jetons et le répertoire de travail pour cette session. Vous pouvez passer un court préfixe de l'ID de session plutôt que le complet.

## Supprimer une session

```bash
anote sessions delete a1b2c3d4
anote sessions rm a1b2c3d4
```

## Prochaines étapes

- [Flux de travail communs](common-workflows.md)
- [Comment Panacea fonctionne](../core-concepts/how-it-works.md) — tours, compactage et comment la longueur de la session affecte le contexte
