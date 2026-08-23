# 測試

## 後端測試

```bash
cd packages/backend
pytest tests/ -v
pytest tests/ --cov=. --cov-report=html  # 帶有覆蓋率
```

測試位於 `packages/backend/tests/`。CI 強制要求覆蓋率 ≥80%。

## CLI 測試

```bash
cd packages/cli
npm test
```

## SDK 測試

```bash
cd packages/sdk
npm test
```

## 端到端

要進行完整的整合測試，使用 Docker 啟動堆疊：

```bash
docker compose up -d
cd packages/backend && pytest tests/integration/ -v
```

## 編寫測試

### Python
遵循 `packages/backend/tests/` 中的現有模式。使用 `pytest` 的 fixtures：

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
使用 Vitest 或 Jest：

```typescript
import { describe, it, expect } from "vitest";
import { myFunction } from "../src/myModule.js";

describe("myFunction", () => {
  it("返回預期的值", () => {
    expect(myFunction("input")).toBe("expected");
  });
});
```
