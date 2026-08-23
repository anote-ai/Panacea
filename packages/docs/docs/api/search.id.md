# API Pencarian

Path dasar: `/api/search`

## Indeks Kode Pencarian

```http
GET /api/search?q=authentication&cwd=/path/to/project&top=10
Authorization: Bearer <token>
```

**Parameter**

| Parameter | Tipe | Deskripsi |
|-----------|------|-----------|
| `q` | string | Kuery pencarian (diperlukan) |
| `cwd` | string | Direktori proyek yang berisi `.anote/index/` |
| `top` | integer | Jumlah hasil yang akan dikembalikan (default: 10) |

**Respons**
```json
{
  "results": [
    {
      "file": "src/auth/handler.py",
      "startLine": 45,
      "endLine": 72,
      "preview": "def authenticate_user(email, password)...",
      "score": 0.8432
    }
  ]
}
```

Mengembalikan `404` jika tidak ada indeks yang ada di `cwd` yang diberikan. Buat indeks terlebih dahulu dengan `anote index`.
