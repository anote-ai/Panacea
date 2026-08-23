# API de Documentos

Caminho base: `/api/documents`

## Fazer Upload de Documento

```http
POST /api/documents/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

file=@document.pdf
```

Formatos suportados: `.pdf`, `.txt`, `.md`, `.docx`, `.csv`

**Resposta**
```json
{
  "id": "doc_abc123",
  "filename": "document.pdf",
  "size": 102400,
  "chunks": 42
}
```

## Listar Documentos

```http
GET /api/documents
Authorization: Bearer <token>
```

## Fazer uma Pergunta

```http
POST /api/documents/{id}/ask
Authorization: Bearer <token>
Content-Type: application/json

{ "question": "Qual é o tópico principal?" }
```

## Deletar Documento

```http
DELETE /api/documents/{id}
Authorization: Bearer <token>
```
