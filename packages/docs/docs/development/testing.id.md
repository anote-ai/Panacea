# Pengujian

## Pengujian Backend

```bash
cd packages/backend
pytest tests/ -v
pytest tests/ --cov=. --cov-report=html  # dengan cakupan
```

Pengujian berada di `packages/backend/tests/`. CI menegakkan cakupan ≥80%.

## Pengujian CLI

```bash
cd packages/cli
npm test
```

## Pengujian SDK

```bash
cd packages/sdk
npm test
```

## End-to-End

Untuk pengujian integrasi penuh, mulai tumpukan dengan Docker:

```bash
docker compose up -d
cd packages/backend && pytest tests/integration/ -v
```

## Menulis Pengujian

### Python
Ikuti pola yang ada di `packages/backend/tests/`. Gunakan fixture `pytest`:

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
Gunakan Vitest atau Jest:

```typescript
import { describe, it, expect } from "vitest";
import { myFunction } from "../src/myModule.js";

describe("myFunction", () => {
  it("returns expected value", () => {
    expect(myFunction("input")).toBe("expected");
  });
});
```
