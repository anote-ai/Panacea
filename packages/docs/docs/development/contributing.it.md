# Contribuire

## Configurazione

```bash
git clone https://github.com/anote-ai/Panacea
cd Panacea

# Installa i pacchetti Node.js
npm install

# Configura il backend Python
cd packages/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Modifica .env con le tue chiavi

# Avvia tutto
cd ../.. 
docker compose up
```

## Flusso di lavoro di sviluppo

1. Crea un branch per la funzionalità da `main`
2. Apporta le tue modifiche nella directory `packages/` pertinente
3. Esegui i test: `make test`
4. Esegui i linters: `make lint`
5. Apri una pull request

## Test

```bash
# Tutti i test
make test

# Solo backend
make test-backend

# Solo TypeScript
make test-ts
```

## Standard di codice

### Python (backend)
- **Ruff** per il linting (`ruff check .`)
- **Mypy** per il controllo dei tipi (`mypy .`)
- **Pytest** per i test (≥80% di copertura)
- Annotare i tipi di tutte le nuove funzioni

### TypeScript (frontend/cli/sdk)
- **ESLint** per il linting
- **Vitest** o **Jest** per i test
- TypeScript rigoroso (`"strict": true`)

## CI

GitHub Actions viene eseguito ad ogni push:
1. Backend: ruff → mypy → pytest (gate di copertura del 80%)
2. TypeScript: build → tests
3. VS Code: build extension
4. Docs: build sito MkDocs
