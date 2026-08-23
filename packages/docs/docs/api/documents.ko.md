# 문서 API

기본 경로: `/api/documents`

## 문서 업로드

```http
POST /api/documents/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

file=@document.pdf
```

지원되는 형식: `.pdf`, `.txt`, `.md`, `.docx`, `.csv`

**응답**
```json
{
  "id": "doc_abc123",
  "filename": "document.pdf",
  "size": 102400,
  "chunks": 42
}
```

## 문서 목록

```http
GET /api/documents
Authorization: Bearer <token>
```

## 질문하기

```http
POST /api/documents/{id}/ask
Authorization: Bearer <token>
Content-Type: application/json

{ "question": "주요 주제가 무엇인가요?" }
```

## 문서 삭제

```http
DELETE /api/documents/{id}
Authorization: Bearer <token>
```
