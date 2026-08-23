# .anote 디렉토리 탐색

Panacea의 CLI는 두 곳에서 구성 정보를 읽습니다: 프로젝트별 파일과 전역 파일입니다.

## 프로젝트 구성

Panacea는 현재 디렉토리에서 위로 검색하여 다음 순서로 첫 번째로 찾은 파일을 사용합니다:

- `.anote.json`
- `.claw.json`
- `anote.config.json`

```json
{
  "model": "claude-sonnet-4-6",
  "permissionMode": "default",
  "maxTurns": 20,
  "compactAfterMessages": 40,
  "hooks": {
    "preToolUse": [],
    "postToolUse": []
  }
}
```

| 키 | 목적 |
|---|---|
| `model` | 이 프로젝트의 기본 모델 |
| `permissionMode` | `default`, `acceptEdits`, 또는 `bypassPermissions` — [권한 모드](../use-panacea/permission-modes.md) 참조 |
| `provider` | 명시적 제공자 재정의 (보통 `model`에서 자동 감지됨) |
| `baseUrl` | OpenAI 호환 엔드포인트의 기본 URL, 예: Ollama의 경우 `http://localhost:11434/v1` |
| `maxTurns` | 세션당 턴 제한 |
| `compactAfterMessages` | 세션 기록을 압축할 시점 |
| `hooks` | `preToolUse` / `postToolUse` 셸 훅 — [Panacea 확장](extend.md) 참조 |

`anote init`는 `.anote.json`을 생성합니다. `anote config`는 이를 읽고 씁니다:

```bash
anote config              # 유효한 구성 표시 (전역 + 로컬)
anote config get model
anote config set model gpt-4.1
anote config path         # 전역 구성 파일 경로 출력
anote config edit         # $EDITOR에서 전역 구성 열기
```

## 전역 구성

`~/.anote/config.json`은 기본값을 보유하고 있으며 — 프로젝트가 이를 재정의하지 않을 때 적용됩니다. 프로젝트 구성은 항상 전역 구성보다 우선합니다.

## CLAW.md

JSON이 아닙니다 — 에이전트가 매 세션 시작 시 프로젝트 컨텍스트를 읽는 마크다운 파일입니다. 무엇이 들어가는지는 [Panacea 확장](extend.md)에서 확인하세요.

## 다음 단계

- [권한 모드](../use-panacea/permission-modes.md)
- [세션 관리](../use-panacea/sessions.md)
