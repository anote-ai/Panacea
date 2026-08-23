# Pruebas

## Pruebas de Backend

```bash
cd packages/backend
pytest tests/ -v
pytest tests/ --cov=. --cov-report=html  # con cobertura
```

Las pruebas están en `packages/backend/tests/`. La CI exige ≥80% de cobertura.

## Pruebas de CLI

```bash
cd packages/cli
npm test
```

## Pruebas de SDK

```bash
cd packages/sdk
npm test
```

## Pruebas de Extremo a Extremo

Para pruebas de integración completas, inicia la pila con Docker:

```bash
docker compose up -d
cd packages/backend && pytest tests/integration/ -v
```

## Escribiendo Pruebas

### Python
Sigue el patrón existente en `packages/backend/tests/`. Usa fixtures de `pytest`:

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
Usa Vitest o Jest:

```typescript
import { describe, it, expect } from "vitest";
import { myFunction } from "../src/myModule.js";

describe("myFunction", () => {
  it("returns expected value", () => {
    expect(myFunction("input")).toBe("expected");
  });
});
```
