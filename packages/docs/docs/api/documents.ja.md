# ドキュメント API

ベースパス: `/api/documents`

## ドキュメントのアップロード

```http
POST /api/documents/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

file=@document.pdf
```

サポートされているフォーマット: `.pdf`, `.txt`, `.md`, `.docx`, `.csv`

**レスポンス**
```json
{
  "id": "doc_abc123",
  "filename": "document.pdf",
  "size": 102400,
  "chunks": 42
}
```

## ドキュメントの一覧

```http
GET /api/documents
Authorization: Bearer <token>
```

## 質問をする

```http
POST /api/documents/{id}/ask
Authorization: Bearer <token>
Content-Type: application/json

{ "question": "主なトピックは何ですか？" }
```

## ドキュメントの削除

```http
DELETE /api/documents/{id}
Authorization: Bearer <token>
```
