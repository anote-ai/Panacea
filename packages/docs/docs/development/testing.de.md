# Testen

## Backend-Tests

```bash
cd packages/backend
pytest tests/ -v
pytest tests/ --cov=. --cov-report=html  # mit Abdeckung
```

Die Tests befinden sich in `packages/backend/tests/`. Die CI erzwingt eine Abdeckung von ≥80%.

## CLI-Tests

```bash
cd packages/cli
npm test
```

## SDK-Tests

```bash
cd packages/sdk
npm test
```

## End-to-End

Für vollständige Integrationstests starten Sie den Stack mit Docker:

```bash
docker compose up -d
cd packages/backend && pytest tests/integration/ -v
```

## Schreiben von Tests

### Python
Folgen Sie dem bestehenden Muster in `packages/backend/tests/`. Verwenden Sie `pytest`-Fixtures:

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
Verwenden Sie Vitest oder Jest:

```typescript
import { describe, it, expect } from "vitest";
import { myFunction } from "../src/myModule.js";

describe("myFunction", () => {
  it("gibt den erwarteten Wert zurück", () => {
    expect(myFunction("input")).toBe("expected");
  });
});
```
