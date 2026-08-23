# Tests

## Tests Backend

```bash
cd packages/backend
pytest tests/ -v
pytest tests/ --cov=. --cov-report=html  # avec couverture
```

Les tests se trouvent dans `packages/backend/tests/`. L'intégration continue impose une couverture ≥80%.

## Tests CLI

```bash
cd packages/cli
npm test
```

## Tests SDK

```bash
cd packages/sdk
npm test
```

## Tests de bout en bout

Pour des tests d'intégration complets, démarrez la pile avec Docker :

```bash
docker compose up -d
cd packages/backend && pytest tests/integration/ -v
```

## Écriture de Tests

### Python
Suivez le modèle existant dans `packages/backend/tests/`. Utilisez les fixtures `pytest` :

```python
import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app({"TESTING": True})
    with app.test_client() as client:
        yield client

def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
```

### TypeScript
Utilisez Vitest ou Jest :

```typescript
import { describe, it, expect } from "vitest";
import { myFunction } from "../src/myModule.js";

describe("myFunction", () => {
  it("returns expected value", () => {
    expect(myFunction("input")).toBe("expected");
  });
});
```
