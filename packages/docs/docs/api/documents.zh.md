# 文档 API

基础路径: `/api/documents`

## 上传文档

```http
POST /api/documents/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

file=@document.pdf
```

支持的格式: `.pdf`, `.txt`, `.md`, `.docx`, `.csv`

**响应**
```json
{
  "id": "doc_abc123",
  "filename": "document.pdf",
  "size": 102400,
  "chunks": 42
}
```

## 列出文档

```http
GET /api/documents
Authorization: Bearer <token>
```

## 提问

```http
POST /api/documents/{id}/ask
Authorization: Bearer <token>
Content-Type: application/json

{ "question": "主要主题是什么？" }
```

## 删除文档

```http
DELETE /api/documents/{id}
Authorization: Bearer <token>
```
