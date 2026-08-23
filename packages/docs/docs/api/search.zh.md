# 搜索 API

基础路径: `/api/search`

## 搜索代码库索引

```http
GET /api/search?q=authentication&cwd=/path/to/project&top=10
Authorization: Bearer <token>
```

**参数**

| 参数      | 类型    | 描述                       |
|-----------|---------|----------------------------|
| `q`      | 字符串  | 搜索查询（必需）           |
| `cwd`    | 字符串  | 包含 `.anote/index/` 的项目目录 |
| `top`    | 整数    | 返回的结果数量（默认: 10） |

**响应**
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

如果在给定的 `cwd` 下不存在索引，则返回 `404`。请先使用 `anote index` 构建索引。
