# 後端 API 概覽

Anote 後端是一個統一的 Flask API，服務所有客戶端界面。

基本 URL: `http://localhost:5000`（本地）或您的部署後端 URL。

## 認證

所有受保護的端點都需要 JWT 權杖：

```
Authorization: Bearer <token>
```

通過 `POST /auth/login` 或 `POST /auth/register` 獲取權杖。

## 主要端點

### 代理聊天（串流）

```
POST /api/chat/stream          # SSE 串流聊天
POST /api/chat                 # 非串流聊天
GET  /api/chat/sessions        # 列出會話
POST /api/chat/sessions        # 創建會話
```

### 文件

```
POST /api/documents/upload     # 上傳文件
GET  /api/documents            # 列出文件
GET  /api/documents/{id}       # 獲取文件
DELETE /api/documents/{id}     # 刪除文件
POST /api/documents/{id}/ask   # 文件問答
```

### 語義搜索

```
GET  /api/search?q=...&cwd=... # 搜索索引的程式碼庫
```

### 認證

```
POST /auth/register            # 註冊
POST /auth/login               # 登入
POST /auth/refresh             # 刷新 JWT
GET  /auth/google              # Google OAuth
```

### 用戶與計費

```
GET  /api/user/profile         # 獲取用戶
POST /api/payments/checkout    # Stripe 結帳
POST /api/payments/portal      # 客戶端入口
POST /api/payments/webhook     # Stripe 網頁鉤子
```
