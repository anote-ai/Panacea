# 網頁應用程式概述

Anote AI 網頁應用程式是一個類似 ChatGPT 的聊天介面，連接到 Anote 後端。

## 功能

- 明亮和黑暗模式（自動檢測系統偏好）
- 通過 SSE 流式響應
- 可摺疊側邊欄中的聊天會話歷史
- 模型選擇器（Claude, GPT-4o 等）
- 文件上傳和問答
- 響應式設計

## 本地運行

```bash
cd packages/web
npm install
npm run dev
```

應用程式運行在 `http://localhost:3000`，並將 API 請求代理到 `http://localhost:5000`。
