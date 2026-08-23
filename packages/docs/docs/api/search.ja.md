# 検索 API

ベースパス: `/api/search`

## コードベースインデックスの検索

```http
GET /api/search?q=authentication&cwd=/path/to/project&top=10
Authorization: Bearer <token>
```

**パラメータ**

| パラメータ | 型     | 説明                                   |
|------------|--------|----------------------------------------|
| `q`       | string | 検索クエリ（必須）                    |
| `cwd`     | string | `.anote/index/` を含むプロジェクトディレクトリ |
| `top`     | integer| 返す結果の数（デフォルト: 10）        |

**レスポンス**
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

指定された `cwd` にインデックスが存在しない場合は `404` を返します。最初に `anote index` でインデックスを構築してください。
