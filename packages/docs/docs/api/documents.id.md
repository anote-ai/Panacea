# API Dokumen

Path dasar: `/api/documents`

## Unggah Dokumen

```http
POST /api/documents/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

file=@document.pdf
```

Format yang didukung: `.pdf`, `.txt`, `.md`, `.docx`, `.csv`

**Respons**
```json
{
  "id": "doc_abc123",
  "filename": "document.pdf",
  "size": 102400,
  "chunks": 42
}
```

## Daftar Dokumen

```http
GET /api/documents
Authorization: Bearer <token>
```

## Ajukan Pertanyaan

```http
POST /api/documents/{id}/ask
Authorization: Bearer <token>
Content-Type: application/json

{ "question": "Apa topik utama?" }
```

## Hapus Dokumen

```http
DELETE /api/documents/{id}
Authorization: Bearer <token>
```
