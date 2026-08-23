# 테스트

## 백엔드 테스트

```bash
cd packages/backend
pytest tests/ -v
pytest tests/ --cov=. --cov-report=html  # 커버리지 포함
```

테스트는 `packages/backend/tests/`에 있습니다. CI는 ≥80% 커버리지를 강제합니다.

## CLI 테스트

```bash
cd packages/cli
npm test
```

## SDK 테스트

```bash
cd packages/sdk
npm test
```

## 종단 간

전체 통합 테스트를 위해 Docker로 스택을 시작합니다:

```bash
docker compose up -d
cd packages/backend && pytest tests/integration/ -v
```

## 테스트 작성

### Python
`packages/backend/tests/`의 기존 패턴을 따르세요. `pytest` 픽스처를 사용하세요:

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
Vitest 또는 Jest를 사용하세요:

```typescript
import { describe, it, expect } from "vitest";
import { myFunction } from "../src/myModule.js";

describe("myFunction", () => {
  it("예상 값을 반환합니다", () => {
    expect(myFunction("input")).toBe("expected");
  });
});
```
