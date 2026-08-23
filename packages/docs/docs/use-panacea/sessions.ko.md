# 세션 관리

모든 `anote chat` 대화는 세션으로 로컬에 저장됩니다 — 메시지, 토큰 사용량 및 작업 디렉토리가 포함됩니다.

## 세션 목록

```bash
anote sessions list
anote sessions ls --limit 50
```

```
저장된 세션 (3):
  a1b2c3d4  12 msgs  in=4,200 out=1,800  10분 전  /Users/you/project
  e5f6a7b8  4 msgs   in=900 out=400      2시간 전   /Users/you/other-project
```

## 세션 보기

```bash
anote sessions show a1b2c3d4
anote sessions show a1b2c3d4 --limit 50   # 더 많은 메시지 기록
```

해당 세션의 대화, 토큰 총계 및 작업 디렉토리를 출력합니다. 전체 세션 ID 대신 세션 ID의 짧은 접두사를 전달할 수 있습니다.

## 세션 삭제

```bash
anote sessions delete a1b2c3d4
anote sessions rm a1b2c3d4
```

## 다음 단계

- [일반 워크플로우](common-workflows.md)
- [Panacea 작동 방식](../core-concepts/how-it-works.md) — 턴, 압축 및 세션 길이가 컨텍스트에 미치는 영향
