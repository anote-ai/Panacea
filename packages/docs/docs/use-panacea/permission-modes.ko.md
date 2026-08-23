# 권한 모드

Panacea는 에이전트가 파일을 작성하거나 명령을 실행하기 전에 묻는지 여부를 제어하는 세 가지 권한 모드를 가지고 있습니다.

| 모드 | 동작 |
|---|---|
| `default` | 파일을 편집하거나 읽기 전용이 아닌 명령을 실행하기 전에 확인합니다 |
| `acceptEdits` | 묻지 않고 파일 편집을 자동으로 수락합니다 |
| `bypassPermissions` | 확인 없이 모든 것을 실행합니다 — 주의해서 사용하세요 |

전역 또는 프로젝트별로 설정할 수 있습니다:

```bash
anote config set permissionMode acceptEdits
```

또는 `.anote.json`에서:

```json
{ "permissionMode": "acceptEdits" }
```

## 명령별 재정의

대부분의 명령은 전역 구성을 수정할 필요가 없습니다 — 동일한 아이디어에 대해 자체 플래그를 사용합니다:

| 플래그 | 사용 가능 | 효과 |
|---|---|---|
| `--auto` | `fix`, `refactor` | 이번 실행에 대해서만 편집을 자동으로 수락합니다 |
| `--dry-run` | `fix`, `docs`, `migrate`, `security`, `perf`, `refactor`, `generate`, `changelog`, `commit`, `review` | 아무것도 쓰지 않고 어떤 일이 발생할지를 보여줍니다 |
| `--no-edit` | `ask` | 읽기 전용 — 에이전트는 원하더라도 파일을 수정할 수 없습니다 |
| `--yes` | `init` | 대화형 프롬프트를 건너뛰고 기본값을 수락합니다 |

`anote fix --loop`는 각 반복마다 묻지 않고 계속 편집해야 하므로 자동으로 `acceptEdits`를 의미합니다.

## 정책 레이어로서의 훅

"묻기 vs. 묻지 않기"보다 더 구체적인 경우 — 특정 경로에 접근하는 `Bash` 호출을 차단하는 것과 같은 — 대신 `preToolUse` 훅을 사용하세요. [Panacea 확장하기](../core-concepts/extend.md)를 참조하세요.

## 다음 단계

- [Panacea 작동 방식](../core-concepts/how-it-works.md) — 이 모드들이 제어하는 에이전트 루프
- [.anote 디렉토리 탐색하기](../core-concepts/anote-directory.md) — `permissionMode`가 구성에 있는 위치
