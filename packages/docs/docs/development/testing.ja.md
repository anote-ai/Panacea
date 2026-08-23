# テスト

## バックエンドテスト

```bash
cd packages/backend
pytest tests/ -v
pytest tests/ --cov=. --cov-report=html  # カバレッジ付き
```

テストは `packages/backend/tests/` にあります。CIは≥80%のカバレッジを強制します。

## CLIテスト

```bash
cd packages/cli
npm test
```

## SDKテスト

```bash
cd packages/sdk
npm test
```

## エンドツーエンド

完全な統合テストのために、Dockerでスタックを起動します：

```bash
docker compose up -d
cd packages/backend && pytest tests/integration/ -v
```

## テストの作成

### Python
`packages/backend/tests/` の既存のパターンに従ってください。`pytest` フィクスチャを使用します：

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
VitestまたはJestを使用します：

```typescript
import { describe, it, expect } from "vitest";
import { myFunction } from "../src/myModule.js";

describe("myFunction", () => {
  it("returns expected value", () => {
    expect(myFunction("input")).toBe("expected");
  });
});
```
