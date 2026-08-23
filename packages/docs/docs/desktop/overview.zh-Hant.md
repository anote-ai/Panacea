# 桌面應用程式概述

Anote AI 桌面應用程式是一個私有的、具離線能力的 AI 助手，使用 Electron 建置。

## 主要特性

- **私有**：所有數據保留在您的機器上
- **具離線能力**：可使用本地 Ollama 模型
- **跨平台**：Windows、macOS、Linux
- **捆綁後端**：Python Flask 後端被打包為獨立可執行檔

## 架構

```
Electron shell
  └─ React 前端 (Vite + Tailwind)
  └─ 捆綁的 Python 後端 (PyInstaller 可執行檔)
       └─ Flask API 在 5099 埠
       └─ SQLite 資料庫 (本地)
       └─ ChromaDB 向量儲存 (本地)
```
