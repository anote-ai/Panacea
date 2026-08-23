# 网页应用概述

Anote AI 网页应用是一个类似 ChatGPT 的聊天界面，连接到 Anote 后端。

## 功能

- 浅色和深色模式（自动检测系统偏好）
- 通过 SSE 流式响应
- 可折叠侧边栏中的聊天会话历史
- 模型选择器（Claude, GPT-4o 等）
- 文档上传和问答
- 响应式设计

## 本地运行

```bash
cd packages/web
npm install
npm run dev
```

该应用运行在 `http://localhost:3000` 并将 API 调用代理到 `http://localhost:5000`。
