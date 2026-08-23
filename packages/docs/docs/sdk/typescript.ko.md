# TypeScript SDK

`@anote-ai/sdk`는 Anote REST API를 위한 타입이 지정된 TypeScript/JavaScript 클라이언트입니다. CLI나 웹 앱을 통해서가 아니라 스크립트, 백엔드 서비스 또는 자신의 앱에서 Anote를 프로그래밍적으로 호출하고 싶을 때 사용하세요.

!!! note "로컬 백엔드와의 통신"
    기본적으로 클라이언트는 `https://api.anote.ai`를 가리킵니다. 이 리포지토리에서 백엔드를 로컬로 실행하는 경우(`docker compose up` 또는 `make dev-backend`), `baseUrl: "http://localhost:5050"` (포트 오버라이드를 사용하지 않는 경우 `:5000`)을 전달하세요 — [시작하기 → 구성](../getting-started/configuration.md)을 참조하세요.

## 필요한 사항

- Node.js 18+
- Anote 계정 ( `POST /auth/register` 또는 웹 앱의 등록 페이지를 통해 등록)
- API 키 (아래 2단계)

## 1. 설치

```bash
npm install @anote-ai/sdk
```

## 2. API 키 받기

API 키에 대한 설정 UI는 아직 없으므로, 백엔드에 직접 요청하여 생성하세요. 먼저 로그인하여 JWT를 얻고, 이를 사용하여 키를 생성합니다:

```bash
# JWT를 얻기 위해 로그인
curl -X POST http://localhost:5050/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "you@example.com", "password": "..."}'
# → { "access_token": "eyJ..." }

# JWT를 사용하여 API 키 생성
curl -X POST http://localhost:5050/api/user/api-keys \
  -H "Authorization: Bearer eyJ..."
# → { "key": "ak-..." }
```

그 `ak-...` 값을 저장하세요 — 생성 시에만 한 번 반환됩니다.

## 3. 클라이언트 초기화

```ts
import { AnoteClient } from "@anote-ai/sdk";

const client = new AnoteClient({
  apiKey: "ak-...",
  baseUrl: "http://localhost:5050", // https://api.anote.ai를 사용하려면 생략
});
```

`apiKey`는 유일한 필수 옵션입니다. 프로덕션 API를 가리킬 때는 `baseUrl`을 생략하세요.

## 4. 첫 번째 메시지 보내기

```ts
const { result, usage } = await client.chat("이 코드베이스를 설명해 주세요");

console.log(result);
console.log(`사용된 ${usage.inputTokens} 입력 / ${usage.outputTokens} 출력 토큰`);
```

`chat()`은 비스트리밍 호출입니다 — 전체 응답을 기다리며, 이는 스크립팅 및 자동화에 적합합니다. 두 번째 인수로 `cwd`, `model` 또는 `tools`를 전달하여 작업 디렉토리, 모델 선택 또는 AI가 사용할 수 있는 도구를 제한할 수 있습니다:

```ts
await client.chat("이 파일의 TODO 목록 나열", {
  cwd: "/path/to/project",
  model: "claude-sonnet-4-6",
  tools: ["Read", "Grep"],
});
```

## 일반 작업

**과거 세션 나열 및 검사**

```ts
const sessions = await client.listSessions();
const { history } = await client.getSessionMessages(sessions[0].sessionId);
```

**세션 기록 검색**

```ts
const { results } = await client.search("인증 로직");
```

**사용량 및 쿼타 확인**

```ts
const usage = await client.getUsage();
console.log(`${usage.remaining.requests} 요청이 남았습니다.`);
```

**세션을 읽기 전용 링크로 공유**

```ts
const { shareUrl } = await client.shareSession(sessions[0].sessionId);
```

**오류 처리**

모든 비 2xx 응답은 `AnoteError`를 발생시키며, 이는 HTTP 상태 및 파싱된 응답 본문을 포함합니다:

```ts
import { AnoteClient, AnoteError } from "@anote-ai/sdk";

try {
  await client.chat("...");
} catch (err) {
  if (err instanceof AnoteError) {
    console.error(err.status, err.message); // 예: 429, "월간 쿼타 초과"
  }
}
```

**서버 상태 확인 (인증 필요 없음)**

```ts
const health = await client.health();
```

## API 참조

### `new AnoteClient(options)`

| 옵션 | 유형 | 필수 | 설명 |
|---|---|---|---|
| `apiKey` | `string` | ✓ | 2단계에서 받은 API 키, `ak-`로 시작 |
| `baseUrl` | `string` | | 서버 URL (기본값: `https://api.anote.ai`) |

### 메서드

| 메서드 | 설명 |
|--------|-------------|
| `chat(message, options?)` | 메시지를 보내고, AI의 완전한 응답을 받습니다 |
| `listSessions()` | 모든 채팅 세션을 나열합니다 |
| `getSessionMessages(id)` | 세션의 메시지 기록을 가져옵니다 |
| `deleteSession(id)` | 세션을 삭제합니다 |
| `shareSession(id)` | 공유 가능한 읽기 전용 링크를 생성합니다 |
| `search(query, limit?)` | 세션 간의 전체 텍스트 검색 |
| `getUsage()` | 현재 월 사용량 + 쿼타 |
| `health()` | 서버 상태 확인 (인증 필요 없음) |

## 다음 단계

- [백엔드 API 개요](../api/overview.md) — 이 SDK의 REST 엔드포인트
- [CLI 개요](../cli/overview.md) — 스크립팅 대신 대화형/터미널 사용을 위한 것
