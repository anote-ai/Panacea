# TypeScript SDK

`@anote-ai/sdk` 是一个用于 Anote REST API 的类型化 TypeScript/JavaScript 客户端。当您想要以编程方式调用 Anote 时 — 从脚本、后端服务或您自己的应用程序 — 而不是通过 CLI 或 Web 应用程序时，请使用它。

!!! note "与本地后端通信"
    默认情况下，客户端指向 `https://api.anote.ai`。如果您在本地运行此代码库中的后端（`docker compose up` 或 `make dev-backend`），请传递 `baseUrl: "http://localhost:5050"`（如果您没有使用端口覆盖，则为 `:5000`） — 请参见 [入门 → 配置](../getting-started/configuration.md)。

## 您需要的

- Node.js 18+
- Anote 账户（通过 `POST /auth/register` 或 Web 应用程序的注册页面注册）
- API 密钥（见下文第 2 步）

## 1. 安装

```bash
npm install @anote-ai/sdk
```

## 2. 获取 API 密钥

目前还没有 API 密钥的设置 UI，因此请直接向后端生成一个。首先登录以获取 JWT，然后使用它创建密钥：

```bash
# 登录以获取 JWT
curl -X POST http://localhost:5050/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "you@example.com", "password": "..."}'
# → { "access_token": "eyJ..." }

# 使用 JWT 生成 API 密钥
curl -X POST http://localhost:5050/api/user/api-keys \
  -H "Authorization: Bearer eyJ..."
# → { "key": "ak-..." }
```

保存该 `ak-...` 值 — 它只在创建时返回一次。

## 3. 初始化客户端

```ts
import { AnoteClient } from "@anote-ai/sdk";

const client = new AnoteClient({
  apiKey: "ak-...",
  baseUrl: "http://localhost:5050", // 省略以使用 https://api.anote.ai
});
```

`apiKey` 是唯一必需的选项。当您指向生产 API 时，可以省略 `baseUrl`。

## 4. 发送您的第一条消息

```ts
const { result, usage } = await client.chat("解释这个代码库");

console.log(result);
console.log(`使用了 ${usage.inputTokens} 输入 / ${usage.outputTokens} 输出令牌`);
```

`chat()` 是非流式调用 — 它等待完整的响应，这正是您在脚本和自动化中所需要的。在第二个参数中传递 `cwd`、`model` 或 `tools` 以限制工作目录、选择模型或限制 AI 可以使用的工具：

```ts
await client.chat("列出此文件中的 TODO", {
  cwd: "/path/to/project",
  model: "claude-sonnet-4-6",
  tools: ["Read", "Grep"],
});
```

## 常见任务

**列出并检查过去的会话**

```ts
const sessions = await client.listSessions();
const { history } = await client.getSessionMessages(sessions[0].sessionId);
```

**在会话历史中搜索**

```ts
const { results } = await client.search("身份验证逻辑");
```

**检查您的使用情况和配额**

```ts
const usage = await client.getUsage();
console.log(`${usage.remaining.requests} 本月剩余请求`);
```

**以只读链接共享会话**

```ts
const { shareUrl } = await client.shareSession(sessions[0].sessionId);
```

**处理错误**

每个非 2xx 响应都会抛出 `AnoteError`，它携带 HTTP 状态和解析后的响应体：

```ts
import { AnoteClient, AnoteError } from "@anote-ai/sdk";

try {
  await client.chat("...");
} catch (err) {
  if (err instanceof AnoteError) {
    console.error(err.status, err.message); // 例如 429, "月配额超出"
  }
}
```

**检查服务器存活性（无需身份验证）**

```ts
const health = await client.health();
```

## API 参考

### `new AnoteClient(options)`

| 选项 | 类型 | 必需 | 描述 |
|---|---|---|---|
| `apiKey` | `string` | ✓ | 第 2 步中的 API 密钥，以 `ak-` 开头 |
| `baseUrl` | `string` | | 服务器 URL（默认: `https://api.anote.ai`） |

### 方法

| 方法 | 描述 |
|--------|-------------|
| `chat(message, options?)` | 发送消息，获取完整的 AI 响应 |
| `listSessions()` | 列出所有聊天会话 |
| `getSessionMessages(id)` | 获取会话的消息历史 |
| `deleteSession(id)` | 删除会话 |
| `shareSession(id)` | 生成可共享的只读链接 |
| `search(query, limit?)` | 在会话中进行全文搜索 |
| `getUsage()` | 当前月份的使用情况 + 配额 |
| `health()` | 服务器存活性检查（无需身份验证） |

## 下一步

- [后端 API 概述](../api/overview.md) — 此 SDK 下面的 REST 端点
- [CLI 概述](../cli/overview.md) — 用于交互式/终端使用，而不是脚本编写
