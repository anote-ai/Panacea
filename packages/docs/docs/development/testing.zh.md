# 测试

## 后端测试

```bash
cd packages/backend
pytest tests/ -v
pytest tests/ --cov=. --cov-report=html  # 带覆盖率
```

测试位于 `packages/backend/tests/`。CI 强制要求覆盖率 ≥80%。

## CLI 测试

```bash
cd packages/cli
npm test
```

## SDK 测试

```bash
cd packages/sdk
npm test
```

## 端到端

要进行完整的集成测试，请使用 Docker 启动堆栈：

```bash
docker compose up -d
cd packages/backend && pytest tests/integration/ -v
```

## 编写测试

### Python
遵循 `packages/backend/tests/` 中的现有模式。使用 `pytest` 固件：

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
  it("返回预期值", () => {
    expect(myFunction("input")).toBe("expected");
  });
});
```
