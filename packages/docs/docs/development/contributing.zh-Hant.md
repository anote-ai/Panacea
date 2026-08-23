# 貢獻

## 設定

```bash
git clone https://github.com/anote-ai/Panacea
cd Panacea

# 安裝 Node.js 套件
npm install

# 設定 Python 後端
cd packages/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# 使用你的金鑰編輯 .env

# 啟動所有服務
cd ../.. 
docker compose up
```

## 開發工作流程

1. 從 `main` 創建一個功能分支
2. 在相關的 `packages/` 目錄中進行更改
3. 執行測試：`make test`
4. 執行代碼檢查：`make lint`
5. 提交拉取請求

## 測試

```bash
# 所有測試
make test

# 僅後端
make test-backend

# 僅 TypeScript
make test-ts
```

## 代碼標準

### Python (後端)
- **Ruff** 用於代碼檢查 (`ruff check .`)
- **Mypy** 用於類型檢查 (`mypy .`)
- **Pytest** 用於測試 (≥80% 覆蓋率)
- 所有新函數必須進行類型註解

### TypeScript (前端/CLI/SDK)
- **ESLint** 用於代碼檢查
- **Vitest** 或 **Jest** 用於測試
- 嚴格的 TypeScript (`"strict": true`)

## CI

GitHub Actions 在每次推送時運行：
1. 後端：ruff → mypy → pytest (80% 覆蓋率門檻)
2. TypeScript：構建 → 測試
3. VS Code：構建擴展
4. 文檔：構建 MkDocs 網站
