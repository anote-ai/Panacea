# 后端 API 概述

Anote 后端是一个统一的 Flask API，服务于所有客户端界面。

基础 URL: `http://localhost:5000`（本地）或您的部署后端 URL。

## 认证

所有受保护的端点都需要 JWT 令牌：

```
Authorization: Bearer <token>
```

通过 `POST /auth/login` 或 `POST /auth/register` 获取令牌。

## 关键端点

### 代理聊天（流式）

```
POST /api/chat/stream          # SSE 流式聊天
POST /api/chat                 # 非流式聊天
GET  /api/chat/sessions        # 列出会话
POST /api/chat/sessions        # 创建会话
```

### 文档

```
POST /api/documents/upload     # 上传文档
GET  /api/documents            # 列出文档
GET  /api/documents/{id}       # 获取文档
DELETE /api/documents/{id}     # 删除文档
POST /api/documents/{id}/ask   # 文档问答
```

### 语义搜索

```
GET  /api/search?q=...&cwd=... # 搜索索引代码库
```

### 认证

```
POST /auth/register            # 注册
POST /auth/login               # 登录
POST /auth/refresh             # 刷新 JWT
GET  /auth/google              # Google OAuth
```

### 用户与账单

```
GET  /api/user/profile         # 获取用户
POST /api/payments/checkout    # Stripe 结账
POST /api/payments/portal      # 客户门户
POST /api/payments/webhook     # Stripe 网络钩子
```
