# API Документов

Базовый путь: `/api/documents`

## Загрузить документ

```http
POST /api/documents/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

file=@document.pdf
```

Поддерживаемые форматы: `.pdf`, `.txt`, `.md`, `.docx`, `.csv`

**Ответ**
```json
{
  "id": "doc_abc123",
  "filename": "document.pdf",
  "size": 102400,
  "chunks": 42
}
```

## Список документов

```http
GET /api/documents
Authorization: Bearer <token>
```

## Задать вопрос

```http
POST /api/documents/{id}/ask
Authorization: Bearer <token>
Content-Type: application/json

{ "question": "Какова основная тема?" }
```

## Удалить документ

```http
DELETE /api/documents/{id}
Authorization: Bearer <token>
```
