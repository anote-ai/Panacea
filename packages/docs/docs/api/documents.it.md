# API Documenti

Percorso base: `/api/documents`

## Carica Documento

```http
POST /api/documents/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

file=@document.pdf
```

Formati supportati: `.pdf`, `.txt`, `.md`, `.docx`, `.csv`

**Risposta**
```json
{
  "id": "doc_abc123",
  "filename": "document.pdf",
  "size": 102400,
  "chunks": 42
}
```

## Elenca Documenti

```http
GET /api/documents
Authorization: Bearer <token>
```

## Fai una Domanda

```http
POST /api/documents/{id}/ask
Authorization: Bearer <token>
Content-Type: application/json

{ "question": "Qual è l'argomento principale?" }
```

## Elimina Documento

```http
DELETE /api/documents/{id}
Authorization: Bearer <token>
```
