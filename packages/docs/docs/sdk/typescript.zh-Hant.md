# TypeScript SDK

`@anote-ai/sdk` 是一個類型化的 TypeScript/JavaScript 客戶端，用於 Anote REST API。當您想要以程式方式調用 Anote 時 — 從腳本、後端服務或您自己的應用程式 — 而不是通過 CLI 或網頁應用程式時，請使用它。

!!! note "與本地後端通訊"
    默認情況下，客戶端指向 `https://api.anote.ai`。如果您在本地運行此倉庫的後端（`docker compose up`，或 `make dev-backend`），請傳遞 `baseUrl: "http://localhost:5050"`（如果您不使用端口覆蓋，則為 `:5000`）— 請參見 [開始使用 → 配置](../getting-started/configuration.md)。

## 您需要的條件

- Node.js 18+
- 一個 Anote 帳戶（通過 `POST /auth/register` 或網頁應用程式的註冊頁面註冊）
- 一個 API 權杖（見下方第 2 步）

## 1. 安裝

```bash
npm install @anote-ai/sdk
```

## 2. 獲取 API 權杖

目前尚無 API 權杖的設置 UI，因此直接對後端進行鑄造。首先登錄以獲取 JWT，然後使用它來創建一個權杖：

```bash
# 登錄以獲取 JWT
curl -X POST http://localhost:5050/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "you@example.com", "password": "..."}'
# → { "access_token": "eyJ..." }

# 使用 JWT 鑄造 API 權杖
curl -X POST http://localhost:5050/api/user/api-keys \
  -H "Authorization: Bearer eyJ..."
# → { "key": "ak-..." }
```

保存該 `ak-...` 值 — 它僅在創建時返回一次。

## 3. 初始化客戶端

```ts
import { AnoteClient } from "@anote-ai/sdk";

const client = new AnoteClient({
  apiKey: "ak-...",
  baseUrl: "http://localhost:5050", // 省略以使用 https://api.anote.ai
});
```

`apiKey` 是唯一的必需選項。當您指向生產 API 時，省略 `baseUrl`。

## 4. 發送您的第一條消息

```ts
const { result, usage } = await client.chat("解釋這個程式碼庫");

console.log(result);
console.log(`使用了 ${usage.inputTokens} 個輸入 / ${usage.outputTokens} 個輸出權杖`);
```

`chat()` 是非串流調用 — 它等待完整的響應，這是您在腳本和自動化中所需的。將 `cwd`、`model` 或 `tools` 作為第二個參數傳遞，以範圍工作目錄、選擇模型或限制 AI 可以使用的工具：

```ts
await client.chat("列出此文件中的 TODO", {
  cwd: "/path/to/project",
  model: "claude-sonnet-4-6",
  tools: ["Read", "Grep"],
});
```

## 常見任務

**列出並檢查過去的工作階段**

```ts
const sessions = await client.listSessions();
const { history } = await client.getSessionMessages(sessions[0].sessionId);
```

**在工作階段歷史中搜索**

```ts
const { results } = await client.search("身份驗證邏輯");
```

**檢查您的使用情況和配額**

```ts
const usage = await client.getUsage();
console.log(`${usage.remaining.requests} 本月剩餘請求`);
```

**將工作階段作為只讀鏈接分享**

```ts
const { shareUrl } = await client.shareSession(sessions[0].sessionId);
```

**處理錯誤**

每個非 2xx 響應都會拋出 `AnoteError`，該錯誤攜帶 HTTP 狀態和解析的響應主體：

```ts
import { AnoteClient, AnoteError } from "@anote-ai/sdk";

try {
  await client.chat("...");
} catch (err) {
  if (err instanceof AnoteError) {
    console.error(err.status, err.message); // 例如 429, "每月配額超過"
  }
}
```

**檢查伺服器存活狀態（無需身份驗證）**

```ts
const health = await client.health();
```

## API 參考

### `new AnoteClient(options)`

| 選項 | 類型 | 必需 | 描述 |
|---|---|---|---|
| `apiKey` | `string` | ✓ | 第 2 步中的 API 權杖，以 `ak-` 開頭 |
| `baseUrl` | `string` | | 伺服器 URL（默認：`https://api.anote.ai`） |

### 方法

| 方法 | 描述 |
|--------|-------------|
| `chat(message, options?)` | 發送消息，獲取完整的 AI 響應 |
| `listSessions()` | 列出所有聊天工作階段 |
| `getSessionMessages(id)` | 獲取工作階段的消息歷史 |
| `deleteSession(id)` | 刪除一個工作階段 |
| `shareSession(id)` | 鑄造可分享的只讀鏈接 |
| `search(query, limit?)` | 在工作階段中進行全文搜索 |
| `getUsage()` | 當前月份的使用情況 + 配額 |
| `health()` | 伺服器存活檢查（無需身份驗證） |

## 下一步

- [後端 API 概述](../api/overview.md) — 此 SDK 底層的 REST 端點
- [CLI 概述](../cli/overview.md) — 用於交互式/終端使用，而不是腳本編寫
