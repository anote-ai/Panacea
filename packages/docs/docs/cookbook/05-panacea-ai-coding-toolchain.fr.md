# Panacea AI Coding Toolchain

Cette recette explique comment l'expérience de codage AI de Panacea est fournie à travers le CLI, le SDK et VS Code.

## Ce que vous apprendrez

- Les différents points d'entrée de codage AI dans Panacea
- Comment le CLI, le SDK et l'extension VS Code se rapportent au backend partagé
- Les principales capacités du produit pour l'assistance au code privé
- Où chercher dans le dépôt pour les détails d'implémentation

## Pourquoi cela importe

Panacea est construit comme un produit unifié avec plusieurs interfaces :

- un **CLI** qui alimente `anote chat`, la recherche de code et la révision de dépôt
- une **extension VS Code** pour l'assistance AI en éditeur
- un **SDK** pour intégrer Panacea dans d'autres applications

Ces interfaces partagent un backend et une couche de raisonnement pilotée par des agents, ce qui rend le produit cohérent à travers les flux de travail de bureau, web et code.

## Fichiers clés de Panacea

| Fichier | Pourquoi cela importe |
|---|---|
| `Panacea/packages/cli` | Implémentation CLI TypeScript pour les flux de travail des développeurs |
| `Panacea/packages/vscode` | Extension VS Code et intégration de chat |
| `Panacea/packages/sdk` | SDK TypeScript pour un accès programmatique |
| `Panacea/packages/backend` | Service backend partagé alimentant toutes les interactions UI et CLI |

## Comment cela fonctionne

- Une action utilisateur de codage commence au CLI, SDK ou extension VS Code.
- La demande est envoyée à l'API backend de Panacea.
- Le backend utilise l'orchestration des agents et les fournisseurs de modèles pour produire des réponses conscientes du code.
- La réponse est renvoyée dans la même interface, avec des suggestions de code, des explications ou des corrections.

## Fonctionnalités utiles du produit

- **CLI** : `anote chat`, recherche de dépôt, révision de code, génération de code et assistance alimentée par des embeddings.
- **VS Code** : chat en ligne, aperçus de différences, actions de code et réponses en streaming.
- **SDK** : un wrapper client pour l'API de Panacea, permettant des intégrations personnalisées.

## Exécutez-le localement

Depuis la racine de l'espace de travail (`anote/panacea`) :

```bash
cd Panacea
cp packages/backend/.env.example packages/backend/.env
docker compose up --build
```

Cela démarre les services backend et frontend partagés.

Dans un autre terminal, exécutez le package CLI :

```bash
cd Panacea/packages/cli
npm install
npm run dev
```

Vous pouvez ensuite utiliser le CLI localement ou le construire avec `npm run build`.

Pour le développement de VS Code, ouvrez `Panacea/packages/vscode` dans VS Code et lancez l'extension avec le débogueur.

## Remarques pour le livre de recettes

Cette recette est utile pour les coéquipiers qui ont besoin d'une vue d'ensemble de haut niveau du produit de codage AI multi-interface de Panacea. Elle peut également orienter les lecteurs vers des fichiers d'implémentation qu'ils peuvent modifier ou étendre.
