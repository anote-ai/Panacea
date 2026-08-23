# 빠른 시작

## 1. 초기화

```bash
anote init
```

이 단계에서는 API 키와 선호하는 LLM 공급자를 설정하는 방법을 안내합니다.

## 2. 질문하기

```bash
# 일반 질문
anote ask "이 코드베이스에서 인증은 어떻게 작동하나요?"

# 파일에 집중하기
anote ask --file src/auth.ts "이것을 설명해 주세요"

# 코드 파이프
cat src/handler.py | anote ask "여기서 잘못될 수 있는 것은 무엇인가요?"
```

## 3. 자동으로 버그 수정하기

```bash
# 테스트가 통과할 때까지 수정하고 반복하기 (최대 5회)
anote fix --loop --max-iterations 5
```

## 4. 의미 검색을 위한 인덱스 생성

```bash
# 코드베이스 인덱싱 (한 번 실행한 후 계속 업데이트)
anote index

# 의미적으로 검색하기
anote search "JWT 토큰 검증"
anote search "데이터베이스 연결 풀"
```

## 5. PR 검토하기

```bash
anote review --pr 42
```

## 6. 변경 로그 생성하기

```bash
anote changelog --since v1.2.0
```
