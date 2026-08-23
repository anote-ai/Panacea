# 搜尋 API

基本路徑: `/api/search`

## 搜尋程式碼庫索引

```http
GET /api/search?q=authentication&cwd=/path/to/project&top=10
Authorization: Bearer <token>
```

**參數**

| 參數      | 類型    | 描述                       |
|-----------|---------|----------------------------|
| `q`      | 字串    | 搜尋查詢（必填）           |
| `cwd`    | 字串    | 包含 `.anote/index/` 的專案目錄 |
| `top`    | 整數    | 要返回的結果數量（預設：10） |

**回應**
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

如果在給定的 `cwd` 中不存在索引，則返回 `404`。請先使用 `anote index` 建立索引。
