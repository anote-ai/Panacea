# Тестирование

## Тесты на стороне сервера

```bash
cd packages/backend
pytest tests/ -v
pytest tests/ --cov=. --cov-report=html  # с покрытием
```

Тесты находятся в `packages/backend/tests/`. CI требует ≥80% покрытия.

## Тесты CLI

```bash
cd packages/cli
npm test
```

## Тесты SDK

```bash
cd packages/sdk
npm test
```

## Конечное тестирование

Для полного интеграционного тестирования запустите стек с помощью Docker:

```bash
docker compose up -d
cd packages/backend && pytest tests/integration/ -v
```

## Написание тестов

### Python
Следуйте существующему шаблону в `packages/backend/tests/`. Используйте фикстуры `pytest`:

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
Используйте Vitest или Jest:

```typescript
import { describe, it, expect } from "vitest";
import { myFunction } from "../src/myModule.js";

describe("myFunction", () => {
  it("returns expected value", () => {
    expect(myFunction("input")).toBe("expected");
  });
});
```
