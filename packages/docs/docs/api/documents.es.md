# API de Documentos

Ruta base: `/api/documents`

## Subir Documento

```http
POST /api/documents/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

file=@document.pdf
```

Formatos soportados: `.pdf`, `.txt`, `.md`, `.docx`, `.csv`

**Respuesta**
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

## Hacer una Pregunta

```http
POST /api/documents/{id}/ask
Authorization: Bearer <token>
Content-Type: application/json

{ "question": "¿Cuál es el tema principal?" }
```

## Eliminar Documento

```http
DELETE /api/documents/{id}
Authorization: Bearer <token>
```
