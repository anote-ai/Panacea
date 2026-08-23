# Testes

## Testes de Backend

```bash
cd packages/backend
pytest tests/ -v
pytest tests/ --cov=. --cov-report=html  # com cobertura
```

Os testes estão em `packages/backend/tests/`. O CI exige ≥80% de cobertura.

## Testes de CLI

```bash
cd packages/cli
npm test
```

## Testes de SDK

```bash
cd packages/sdk
npm test
```

## Teste de Integração

Para testes de integração completos, inicie a pilha com Docker:

```bash
docker compose up -d
cd packages/backend && pytest tests/integration/ -v
```

## Escrevendo Testes

### Python
Siga o padrão existente em `packages/backend/tests/`. Use fixtures do `pytest`:

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
Use Vitest ou Jest:

```typescript
import { describe, it, expect } from "vitest";
import { myFunction } from "../src/myModule.js";

describe("myFunction", () => {
  it("returns expected value", () => {
    expect(myFunction("input")).toBe("expected");
  });
});
```
