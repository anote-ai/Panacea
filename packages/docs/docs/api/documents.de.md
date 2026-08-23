# Dokumente API

Basis-Pfad: `/api/documents`

## Dokument hochladen

```http
POST /api/documents/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

file=@document.pdf
```

Unterstützte Formate: `.pdf`, `.txt`, `.md`, `.docx`, `.csv`

**Antwort**
```json
{
  "id": "doc_abc123",
  "filename": "document.pdf",
  "size": 102400,
  "chunks": 42
}
```

## Dokumente auflisten

```http
GET /api/documents
Authorization: Bearer <token>
```

## Eine Frage stellen

```http
POST /api/documents/{id}/ask
Authorization: Bearer <token>
Content-Type: application/json

{ "question": "Was ist das Hauptthema?" }
```

## Dokument löschen

```http
DELETE /api/documents/{id}
Authorization: Bearer <token>
```
