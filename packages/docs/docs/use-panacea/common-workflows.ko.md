# 일반적인 작업 흐름

Panacea의 CLI를 사용한 일상적인 작업에 대한 단계별 패턴입니다.

## 익숙하지 않은 코드베이스 탐색

```bash
anote explain                       # CODEBASE.md 투어 생성
anote explain src/auth.ts "이것은 어떻게 작동하나요?"
anote index && anote search "JWT validation"
```

인수가 없는 `explain`은 전체 리포지토리에 대한 `CODEBASE.md` 개요를 작성합니다. 파일을 지정하거나 특정 질문을 하여 더 깊이 들어가세요.

## 버그 수정

```bash
anote fix --error "TypeError: cannot read property 'id' of undefined"
anote fix src/handler.ts "웹훅 핸들러가 부하에서 이벤트를 드롭합니다"
anote fix --loop --cmd "npm test"          # 테스트가 통과할 때까지 반복
```

## 작성 및 커밋

```bash
anote generate "Express용 속도 제한 미들웨어" -o src/middleware/rateLimit.ts
anote test src/middleware/rateLimit.ts --write
anote commit                                # AI 생성 커밋 메시지
```

## 푸시하기 전에 검토

```bash
anote diff --staged                         # 스테이징된 변경 사항 검토
anote review --pr 42                        # 또는 열린 GitHub PR 검토
anote security --severity high              # OWASP Top 10 감사
```

## 풀 요청 열기

```bash
anote pr --gh                               # 설명 생성, gh CLI로 열기
```

## 안전하게 리팩토링

```bash
anote refactor src/legacy.ts "검증 로직을 별도의 함수로 추출" --dry-run
anote refactor src/legacy.ts "검증 로직을 별도의 함수로 추출" --auto
```

아직 검토하지 않은 모든 것에 대해 항상 먼저 `--dry-run`을 시도하세요.

## 다른 작업을 하면서 계속 작업하기

```bash
anote watch "src/**/*.ts"                   # 저장할 때마다 재분석
```

## 진행하면서 문서화하기

```bash
anote docs src/api.ts --style jsdoc
anote changelog --since v1.2.0
```

## 다음 단계

- [프롬프트 라이브러리](prompt-library.md) — 시작점 복사-붙여넣기
- [CLI 명령어](../cli/commands.md) — 전체 플래그 참조
