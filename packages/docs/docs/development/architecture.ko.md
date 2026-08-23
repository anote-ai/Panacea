# 아키텍처

## 모노레포 구조

```
Panacea/
├── packages/
│   ├── backend/    # Python Flask — 통합 API + 에이전트 스트리밍 + RAG
│   ├── cli/        # TypeScript — anote 터미널 CLI
│   ├── vscode/     # TypeScript — VS Code 확장
│   ├── web/        # TypeScript/React — 브라우저 챗봇 앱
│   ├── mobile/     # TypeScript/React Native (Expo) — iOS + Android
│   ├── desktop/    # TypeScript/Electron — 개인 데스크탑 앱
│   ├── sdk/        # TypeScript — JS/TS 클라이언트 SDK
│   └── docs/       # MkDocs Material — 문서 사이트
├── docker-compose.yml
├── package.json    # npm 작업 공간
└── Makefile
```

## 백엔드 아키텍처

Python Flask 백엔드는 모든 서버 측 논리를 처리합니다:

```
packages/backend/
├── app.py                    # Flask 진입점, 라우트 등록
├── api_endpoints/
│   ├── chat/                 # 에이전트 스트리밍 (SSE), 세션 관리
│   ├── documents/            # 업로드, RAG 파이프라인, Q&A
│   ├── search/               # 의미 기반 검색 인덱스 쿼리
│   ├── auth/                 # JWT, Google OAuth
│   ├── user/                 # 프로필, 설정
│   └── payments/             # Stripe 웹훅 + 체크아웃
├── agents/                   # LangChain/LangGraph 에이전트 정의
├── services/
│   ├── rag.py                # 문서 청크화 + Chroma 임베딩
│   ├── streaming.py          # Claude/OpenAI/Gemini에 대한 SSE 스트리밍
│   └── search.py             # TF-IDF 의미 기반 검색
├── database/
│   ├── db.py                 # MySQL 연결 + 쿼리
│   └── schema.sql            # 데이터베이스 스키마
└── models/                   # LLM 제공자 래퍼
```

## 데이터 흐름: 에이전트 챗

```
클라이언트 (CLI / VS Code / 웹 / 모바일)
    │  POST /api/chat/stream {message, cwd, model}
    ▼
Flask 백엔드 (app.py → chat/handler.py)
    │  SSE 스트림
    ▼
LLM 제공자 (Anthropic / OpenAI / Gemini / Ollama)
    │  도구 호출 ↔ 실행 (읽기/쓰기/편집/Bash/Glob/Grep)
    ▼
파일 시스템 (cwd) + Chroma (RAG 컨텍스트)
```

## 기술 선택

| 레이어 | 기술 | 이유 |
|---|---|---|
| 백엔드 | Python Flask | 풍부한 ML/AI 생태계, 기존 에이전트 |
| 에이전트 스트리밍 | Anthropic Python SDK | 네이티브 SSE, 도구 사용 |
| 벡터 DB | ChromaDB | 로컬 우선, 인프라 필요 없음 |
| 데이터베이스 | MySQL | ACID, 기존 스키마 |
| 캐시 | Redis | 세션 + 속도 제한 |
| 프론트엔드 | React 18 + TypeScript | 타입 안전성, 생태계 |
| 데스크탑 | Electron | 크로스 플랫폼, Python 번들 |
| 모바일 | Expo (React Native) | 웹과 코드 공유 |
| CLI | Commander.js | 성숙, TypeScript 친화적 |
| 문서 | MkDocs Material | 아름답고 빠르며, 마크다운 |
