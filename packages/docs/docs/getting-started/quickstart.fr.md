# Démarrage rapide

## 1. Initialiser

```bash
anote init
```

Cela vous guide à travers la configuration de votre clé API et du fournisseur LLM préféré.

## 2. Poser une question

```bash
# Question générale
anote ask "comment fonctionne l'authentification dans cette base de code ?"

# Se concentrer sur un fichier
anote ask --file src/auth.ts "explique ceci"

# Pipeliner le code
cat src/handler.py | anote ask "qu'est-ce qui pourrait mal se passer ici ?"
```

## 3. Corriger les bogues automatiquement

```bash
# Corriger et itérer jusqu'à ce que les tests passent (jusqu'à 5 tours)
anote fix --loop --max-iterations 5
```

## 4. Indexer pour la recherche sémantique

```bash
# Indexer votre base de code (exécuter une fois, puis maintenir à jour)
anote index

# Rechercher sémantiquement
anote search "validation de jeton JWT"
anote search "pool de connexions à la base de données"
```

## 5. Réviser une PR

```bash
anote review --pr 42
```

## 6. Générer un changelog

```bash
anote changelog --since v1.2.0
```
