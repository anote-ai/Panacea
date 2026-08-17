# Panacea 확장하기

프로젝트에서 Panacea의 동작을 사용자 정의하는 두 가지 방법: 지속적인 지침을 위한 **CLAW.md**, 그리고 도구 호출 전후에 자체 명령을 실행하기 위한 **훅**입니다.

## CLAW.md — 프로젝트 메모리

`CLAW.md`는 Panacea가 프로젝트 컨텍스트를 위해 읽는 마크다운 파일입니다 — 사람이 아닌 에이전트를 대상으로 한 README와 같은 개념입니다. `anote init`은 감지된 스택과 검증 명령(test/lint/build)으로 미리 채워진 파일을 자동으로 생성합니다:

```markdown
# CLAW.md

This file provides guidance to Anote AI when working with code in this repository.

## Project overview

<!-- Describe what this project does -->

## Stack

TypeScript · Next.js

## Verification

Run these before considering a change complete:

  npm test
  npm run lint

## Working agreement

- Read relevant files before making changes
- Run the verification commands after modifying logic
- Keep changes small and focused
- Prefer editing existing files over creating new ones
```

자유롭게 편집하세요 — 아키텍처 메모, 규칙, 또는 에이전트가 계속 실수하는 부분을 추가하세요. Panacea는 해당 디렉터리에서 세션을 시작할 때마다 이 파일을 읽습니다.

## 훅 — 도구 호출 전후에 자체 명령 실행하기

훅은 각 도구 호출 전(`preToolUse`) 또는 후(`postToolUse`)에 셸 명령을 실행하며, `.anote.json`에서 설정합니다:

```json
{
  "hooks": {
    "preToolUse": ["./scripts/check-tool-policy.sh"],
    "postToolUse": ["npx prettier --write ."]
  }
}
```

**종료 코드 의미:**

| 종료 코드 | 효과 |
|---|---|
| `0` | 허용 — stdout이 안내 메시지로 캡처됨 |
| `2` | 거부 — stdout이 이유로 캡처되어 에이전트에 표시됨 |
| 그 외 | 경고하지만 허용 |

`preToolUse`를 사용해 위험한 명령을 차단하거나 실행 전에 정책을 적용하세요. `postToolUse`는 편집할 때마다 자동 포맷팅하는 등의 용도로 사용하세요.

## 다음 단계

- [.anote 디렉터리 살펴보기](anote-directory.md) — CLAW.md와 설정이 위치하는 곳
- [권한 모드](../use-panacea/permission-modes.md) — 에이전트가 할 수 있는 일을 제어하는 또 다른 수단
