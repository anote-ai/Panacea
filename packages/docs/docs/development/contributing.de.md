# Mitwirken

## Einrichtung

```bash
git clone https://github.com/anote-ai/Panacea
cd Panacea

# Installiere Node.js-Pakete
npm install

# Richte das Python-Backend ein
cd packages/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Bearbeite .env mit deinen Schlüsseln

# Starte alles
cd ../.. 
docker compose up
```

## Entwicklungs-Workflow

1. Erstelle einen Feature-Branch von `main`
2. Nimm deine Änderungen im entsprechenden `packages/` Verzeichnis vor
3. Führe Tests aus: `make test`
4. Führe Linter aus: `make lint`
5. Öffne einen Pull-Request

## Testen

```bash
# Alle Tests
make test

# Nur Backend
make test-backend

# Nur TypeScript
make test-ts
```

## Code-Standards

### Python (Backend)
- **Ruff** für Linting (`ruff check .`)
- **Mypy** für Typüberprüfung (`mypy .`)
- **Pytest** für Tests (≥80% Abdeckung)
- Typannotiere alle neuen Funktionen

### TypeScript (Frontend/CLI/SDK)
- **ESLint** für Linting
- **Vitest** oder **Jest** für Tests
- Strenges TypeScript (`"strict": true`)

## CI

GitHub Actions wird bei jedem Push ausgeführt:
1. Backend: ruff → mypy → pytest (80% Abdeckungsgrenze)
2. TypeScript: build → tests
3. VS Code: Erweiterung erstellen
4. Docs: MkDocs-Website erstellen
