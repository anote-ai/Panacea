# 프롬프트 라이브러리

`anote ask`, `anote chat`, 및 `anote fix`에 대한 프롬프트를 작업별로 정리하여 복사하여 붙여넣기 합니다.

## 코드 이해하기

```bash
anote ask "이 코드베이스는 대체 무엇을 하나요?"
anote ask --file src/payments/webhook.ts "이 파일을 한 줄씩 설명해 주세요"
anote ask "레이트 리미터는 어디에 설정되어 있으며, 한계는 무엇인가요?"
anote ask "여기서 캐싱 레이어를 제거하면 무엇이 깨질까요?"
```

## 디버깅

```bash
anote fix --error "$(cat error.log)"
anote ask "왜 이 테스트가 간헐적으로 실패하나요, 하지만 일관되게는 실패하지 않나요?"
anote fix src/db/pool.ts "연결이 풀로 다시 반환되지 않고 있습니다"
```

## 코드 리뷰

```bash
anote review --file src/auth/session.ts
anote review --pr 42
anote diff --staged -c "오류 처리 및 엣지 케이스에 집중하세요"
```

## 리팩토링

```bash
anote refactor src/utils.ts "이것을 더 작고 단일 목적의 함수로 나누세요" --dry-run
anote ask "이 논리를 표현하는 더 간단한 방법이 있나요?" --file src/parser.ts
anote migrate --from "moment" --to "date-fns"
```

## 테스트 작성하기

```bash
anote test src/utils/validate.ts --coverage --write
anote ask "이 함수에 대해 내가 놓치고 있는 엣지 케이스는 무엇인가요?" --file src/utils/validate.ts
```

## 보안 및 성능

```bash
anote security --severity high
anote perf --focus "데이터베이스, 번들 크기"
```

## 문서화

```bash
anote docs src/api/client.ts --style jsdoc
anote changelog --since v1.2.0
anote explain --stdout                       # 빠른 아키텍처 요약
```

## 다음 단계

- [일반적인 워크플로우](common-workflows.md)
- [CLI 명령어](../cli/commands.md)
