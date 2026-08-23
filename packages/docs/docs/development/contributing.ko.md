# 기여하기

## 설정

```bash
git clone https://github.com/anote-ai/Panacea
cd Panacea

# Node.js 패키지 설치
npm install

# Python 백엔드 설정
cd packages/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# .env 파일을 당신의 키로 수정하세요

# 모든 시작
cd ../.. 
docker compose up
```

## 개발 워크플로우

1. `main`에서 기능 브랜치 생성
2. 관련 `packages/` 디렉토리에서 변경 사항 적용
3. 테스트 실행: `make test`
4. 린터 실행: `make lint`
5. 풀 리퀘스트 열기

## 테스트

```bash
# 모든 테스트
make test

# 백엔드만
make test-backend

# TypeScript만
make test-ts
```

## 코드 표준

### Python (백엔드)
- **Ruff** 린팅용 (`ruff check .`)
- **Mypy** 타입 검사용 (`mypy .`)
- **Pytest** 테스트용 (≥80% 커버리지)
- 모든 새로운 함수에 타입 주석 추가

### TypeScript (프론트엔드/CLI/SDK)
- **ESLint** 린팅용
- **Vitest** 또는 **Jest** 테스트용
- 엄격한 TypeScript (`"strict": true`)

## CI

GitHub Actions는 모든 푸시에서 실행됩니다:
1. 백엔드: ruff → mypy → pytest (80% 커버리지 게이트)
2. TypeScript: 빌드 → 테스트
3. VS Code: 확장 빌드
4. 문서: MkDocs 사이트 빌드
