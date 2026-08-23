# TypeScript SDK

`@anote-ai/sdk` は、Anote REST API の型付き TypeScript/JavaScript クライアントです。CLI やウェブアプリを介さずに、スクリプト、バックエンドサービス、または独自のアプリから Anote をプログラム的に呼び出したい場合に使用します。

!!! note "ローカルバックエンドとの対話"
    デフォルトでは、クライアントは `https://api.anote.ai` を指しています。このリポジトリからバックエンドをローカルで実行している場合（`docker compose up` または `make dev-backend`）、`baseUrl: "http://localhost:5050"`（ポートオーバーライドを使用していない場合は `:5000`）を渡してください — 詳細は [はじめに → 設定](../getting-started/configuration.md) を参照してください。

## 必要なもの

- Node.js 18+
- Anote アカウント（`POST /auth/register` またはウェブアプリの登録ページから登録）
- API キー（以下のステップ 2）

## 1. インストール

```bash
npm install @anote-ai/sdk
```

## 2. API キーを取得

API キーの設定 UI はまだないため、バックエンドに対して直接ミントします。まず、JWT を取得するためにログインし、それを使用してキーを作成します：

```bash
# JWT を取得するためにログイン
curl -X POST http://localhost:5050/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "you@example.com", "password": "..."}'
# → { "access_token": "eyJ..." }

# JWT を使用して API キーをミント
curl -X POST http://localhost:5050/api/user/api-keys \
  -H "Authorization: Bearer eyJ..."
# → { "key": "ak-..." }
```

その `ak-...` 値を保存してください — 作成時にのみ返されます。

## 3. クライアントを初期化

```ts
import { AnoteClient } from "@anote-ai/sdk";

const client = new AnoteClient({
  apiKey: "ak-...",
  baseUrl: "http://localhost:5050", // https://api.anote.ai を使用するには省略
});
```

`apiKey` は唯一の必須オプションです。プロダクション API を指している場合は `baseUrl` を省略してください。

## 4. 最初のメッセージを送信

```ts
const { result, usage } = await client.chat("このコードベースを説明してください");

console.log(result);
console.log(`今月の残りリクエスト数: ${usage.inputTokens} 入力 / ${usage.outputTokens} 出力トークン`);
```

`chat()` は非ストリーミング呼び出しです — 完全な応答を待機します。これはスクリプトや自動化に必要なものです。作業ディレクトリをスコープするために、2 番目の引数に `cwd`、モデルを選択するために `model`、または AI が使用できるツールを制限するために `tools` を渡します：

```ts
await client.chat("このファイルの TODO をリストアップ", {
  cwd: "/path/to/project",
  model: "claude-sonnet-4-6",
  tools: ["Read", "Grep"],
});
```

## 一般的なタスク

**過去のセッションをリストして確認**

```ts
const sessions = await client.listSessions();
const { history } = await client.getSessionMessages(sessions[0].sessionId);
```

**セッション履歴を横断的に検索**

```ts
const { results } = await client.search("認証ロジック");
```

**使用状況とクォータを確認**

```ts
const usage = await client.getUsage();
console.log(`${usage.remaining.requests} 件のリクエストが今月残っています`);
```

**セッションを読み取り専用リンクとして共有**

```ts
const { shareUrl } = await client.shareSession(sessions[0].sessionId);
```

**エラーを処理**

すべての非 2xx 応答は `AnoteError` をスローし、HTTP ステータスと解析された応答ボディを持ちます：

```ts
import { AnoteClient, AnoteError } from "@anote-ai/sdk";

try {
  await client.chat("...");
} catch (err) {
  if (err instanceof AnoteError) {
    console.error(err.status, err.message); // 例: 429, "月間クォータを超えました"
  }
}
```

**サーバーの生存確認（認証不要）**

```ts
const health = await client.health();
```

## API リファレンス

### `new AnoteClient(options)`

| オプション | 型 | 必須 | 説明 |
|---|---|---|---|
| `apiKey` | `string` | ✓ | ステップ 2 の API キー、`ak-` で始まる |
| `baseUrl` | `string` | | サーバーの URL（デフォルト: `https://api.anote.ai`） |

### メソッド

| メソッド | 説明 |
|--------|-------------|
| `chat(message, options?)` | メッセージを送信し、完全な AI 応答を取得 |
| `listSessions()` | すべてのチャットセッションをリスト |
| `getSessionMessages(id)` | セッションのメッセージ履歴を取得 |
| `deleteSession(id)` | セッションを削除 |
| `shareSession(id)` | 共有可能な読み取り専用リンクをミント |
| `search(query, limit?)` | セッション間の全文検索 |
| `getUsage()` | 現在の月の使用状況 + クォータ |
| `health()` | サーバーの生存確認（認証不要） |

## 次のステップ

- [バックエンド API 概要](../api/overview.md) — この SDK の下にある REST エンドポイント
- [CLI 概要](../cli/overview.md) — スクリプトの代わりにインタラクティブ/ターミナルで使用するためのもの
