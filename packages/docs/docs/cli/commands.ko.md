# CLI 명령어

## `anote ask`

코드에 대한 질문을 하세요.

```bash
anote ask "인증 미들웨어는 어떻게 작동하나요?"
anote ask --file src/auth.ts "이 파일을 설명해 주세요"
anote ask --compare  # 여러 모델 간의 나란히 비교
cat file.py | anote ask "버그를 찾아주세요"
```

## `anote fix`

현재 디렉토리의 버그를 수정하세요.

```bash
anote fix
anote fix --loop                    # 테스트가 통과할 때까지 반복
anote fix --max-iterations 5        # 반복 횟수 제한
anote fix --file src/broken.ts      # 특정 파일 수정
```

## `anote review`

버그, 보안 문제 및 품질을 검토하세요.

```bash
anote review                        # 현재 디렉토리 검토
anote review --file src/handler.ts  # 특정 파일 검토
anote review --pr 42                # GitHub PR에 AI 검토 게시
```

## `anote index`

코드베이스의 TF-IDF 의미 검색 인덱스를 구축하세요.

```bash
anote index              # 현재 디렉토리 인덱싱
anote index --watch      # 변경 사항을 감시하고 재인덱싱
anote index /path/to/dir # 특정 디렉토리 인덱싱
```

## `anote search`

인덱싱된 코드베이스를 의미적으로 검색하세요.

```bash
anote search "JWT 토큰 검증"
anote search "데이터베이스 연결" --top 10
anote search "인증 미들웨어" --json
```

## `anote doctor`

환경의 구성 문제를 확인하세요.

```bash
anote doctor
```

확인 사항: Node.js ≥ 18, `ANTHROPIC_API_KEY` 설정, `.anote.json` 존재, `CLAW.md` 존재, git 설치됨.

## `anote changelog`

git 기록에서 CHANGELOG.md 항목을 생성하세요.

```bash
anote changelog
anote changelog --since v1.2.0
anote changelog --dry-run
```

## `anote docs`

문서화되지 않은 코드에 대한 문서를 생성하세요.

```bash
anote docs
anote docs src/api.ts
anote docs --style jsdoc
anote docs --dry-run
```

## `anote migrate`

AI 지원 코드베이스 마이그레이션.

```bash
anote migrate --from "React 17" --to "React 18"
anote migrate --from "axios" --to "fetch"
anote migrate --dry-run
```

## `anote security`

코드베이스의 보안 감사 (OWASP Top 10).

```bash
anote security
anote security --severity high
anote security --fix
```

## `anote perf`

성능 분석.

```bash
anote perf
anote perf --focus "database,bundle"
anote perf --fix
```
