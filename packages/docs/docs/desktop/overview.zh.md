# 桌面应用程序概述

Anote AI 桌面应用程序是一个私有的、具备离线能力的 AI 助手，基于 Electron 构建。

## 主要特性

- **私有**：所有数据保留在您的机器上
- **离线能力**：与本地 Ollama 模型一起工作
- **跨平台**：Windows、macOS、Linux
- **捆绑后端**：Python Flask 后端打包为独立可执行文件

## 架构

```
Electron shell
  └─ React 前端 (Vite + Tailwind)
  └─ 捆绑的 Python 后端 (PyInstaller 可执行文件)
       └─ 端口 5099 上的 Flask API
       └─ SQLite 数据库（本地）
       └─ ChromaDB 向量存储（本地）
```
