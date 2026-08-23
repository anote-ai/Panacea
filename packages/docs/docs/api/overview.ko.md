# 백엔드 API 개요

Anote 백엔드는 모든 클라이언트 인터페이스에 서비스를 제공하는 통합 Flask API입니다.

기본 URL: `http://localhost:5000` (로컬) 또는 배포된 백엔드 URL.

## 인증

모든 보호된 엔드포인트는 JWT 토큰을 필요로 합니다:

```
Authorization: Bearer <token>
```

토큰은 `POST /auth/login` 또는 `POST /auth/register`를 통해 얻을 수 있습니다.

## 주요 엔드포인트

### 에이전트 채팅 (스트리밍)

```
POST /api/chat/stream          # SSE 스트리밍 채팅
POST /api/chat                 # 비스트리밍 채팅
GET  /api/chat/sessions        # 세션 목록
POST /api/chat/sessions        # 세션 생성
```

### 문서

```
POST /api/documents/upload     # 문서 업로드
GET  /api/documents            # 문서 목록
GET  /api/documents/{id}       # 문서 가져오기
DELETE /api/documents/{id}     # 문서 삭제
POST /api/documents/{id}/ask   # 문서에 대한 Q&A
```

### 의미 검색

```
GET  /api/search?q=...&cwd=... # 인덱스된 코드베이스 검색
```

### 인증

```
POST /auth/register            # 등록
POST /auth/login               # 로그인
POST /auth/refresh             # JWT 갱신
GET  /auth/google              # Google OAuth
```

### 사용자 및 청구

```
GET  /api/user/profile         # 사용자 가져오기
POST /api/payments/checkout    # Stripe 체크아웃
POST /api/payments/portal      # 고객 포털
POST /api/payments/webhook     # Stripe 웹훅
```
