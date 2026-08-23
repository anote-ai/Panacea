# Test

## Test Backend

```bash
cd packages/backend
pytest tests/ -v
pytest tests/ --cov=. --cov-report=html  # con copertura
```

I test si trovano in `packages/backend/tests/`. Il CI richiede una copertura ≥80%.

## Test CLI

```bash
cd packages/cli
npm test
```

## Test SDK

```bash
cd packages/sdk
npm test
```

## End-to-End

Per il test di integrazione completo, avvia il stack con Docker:

```bash
docker compose up -d
cd packages/backend && pytest tests/integration/ -v
```

## Scrivere Test

### Python
Segui il modello esistente in `packages/backend/tests/`. Usa i fixture di `pytest`:

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
