# 文件 API

基本路徑: `/api/documents`

## 上傳文件

```http
POST /api/documents/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

file=@document.pdf
```

支援的格式: `.pdf`, `.txt`, `.md`, `.docx`, `.csv`

**回應**
```json
{
  "id": "doc_abc123",
  "filename": "document.pdf",
  "size": 102400,
  "chunks": 42
}
```

## 列出文件

```http
GET /api/documents
Authorization: Bearer <token>
```

## 提問

```http
POST /api/documents/{id}/ask
Authorization: Bearer <token>
Content-Type: application/json

{ "question": "主要主題是什麼？" }
```

## 刪除文件

```http
DELETE /api/documents/{id}
Authorization: Bearer <token>
```
