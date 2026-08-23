# API des Documents

Chemin de base : `/api/documents`

## Télécharger un Document

```http
POST /api/documents/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

file=@document.pdf
```

Formats pris en charge : `.pdf`, `.txt`, `.md`, `.docx`, `.csv`

**Réponse**
```json
{
  "id": "doc_abc123",
  "filename": "document.pdf",
  "size": 102400,
  "chunks": 42
}
```

## Lister les Documents

```http
GET /api/documents
Authorization: Bearer <token>
```

## Poser une Question

```http
POST /api/documents/{id}/ask
Authorization: Bearer <token>
Content-Type: application/json

{ "question": "Quel est le sujet principal ?" }
```

## Supprimer un Document

```http
DELETE /api/documents/{id}
Authorization: Bearer <token>
```
