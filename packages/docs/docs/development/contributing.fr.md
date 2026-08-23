# Contribuer

## Configuration

```bash
git clone https://github.com/anote-ai/Panacea
cd Panacea

# Installer les paquets Node.js
npm install

# Configurer le backend Python
cd packages/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Modifier .env avec vos clés

# Démarrer tout
cd ../.. 
docker compose up
```

## Flux de développement

1. Créez une branche de fonctionnalité à partir de `main`
2. Apportez vos modifications dans le répertoire `packages/` pertinent
3. Exécutez les tests : `make test`
4. Exécutez les linters : `make lint`
5. Ouvrez une demande de tirage

## Tests

```bash
# Tous les tests
make test

# Backend uniquement
make test-backend

# TypeScript uniquement
make test-ts
```

## Normes de code

### Python (backend)
- **Ruff** pour le linting (`ruff check .`)
- **Mypy** pour la vérification de type (`mypy .`)
- **Pytest** pour les tests (≥80% de couverture)
- Annoter tous les nouvelles fonctions avec des types

### TypeScript (frontend/cli/sdk)
- **ESLint** pour le linting
- **Vitest** ou **Jest** pour les tests
- TypeScript strict (`"strict": true`)

## CI

Les GitHub Actions s'exécutent à chaque push :
1. Backend : ruff → mypy → pytest (seuil de couverture de 80%)
2. TypeScript : build → tests
3. VS Code : construire l'extension
4. Docs : construire le site MkDocs
