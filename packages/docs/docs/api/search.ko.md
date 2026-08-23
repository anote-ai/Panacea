# 검색 API

기본 경로: `/api/search`

## 코드베이스 색인 검색

```http
GET /api/search?q=authentication&cwd=/path/to/project&top=10
Authorization: Bearer <token>
```

**매개변수**

| 매개변수 | 유형 | 설명 |
|-----------|------|-------------|
| `q` | 문자열 | 검색 쿼리 (필수) |
| `cwd` | 문자열 | `.anote/index/`가 포함된 프로젝트 디렉토리 |
| `top` | 정수 | 반환할 결과 수 (기본값: 10) |

**응답**
```json
{
  "results": [
    {
      "file": "src/auth/handler.py",
      "startLine": 45,
      "endLine": 72,
      "preview": "def authenticate_user(email, password)...",
      "score": 0.8432
    }
  ]
}
```

주어진 `cwd`에 색인이 존재하지 않으면 `404`를 반환합니다. 먼저 `anote index`로 색인을 생성하세요.
