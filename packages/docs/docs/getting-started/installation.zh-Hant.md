# 安裝

## CLI

```bash
npm install -g @anote-ai/anote
```

需要 Node.js 18 或更高版本。

## VS Code 擴充功能

在 VS Code 擴充功能市場中搜尋 **"Anote"**，或透過以下方式安裝：

```bash
code --install-extension anote-ai.anote-ai-coding
```

## 網頁應用程式（自我託管）

```bash
git clone https://github.com/anote-ai/Panacea
cd Panacea
cp packages/backend/.env.example packages/backend/.env
# 使用您的 API 金鑰編輯 .env
docker compose up
```

前端: http://localhost:3000 · 後端: http://localhost:5000

## 桌面應用程式

從 [GitHub Releases](https://github.com/anote-ai/Panacea/releases) 下載最新版本。

適用於: **macOS** (DMG), **Windows** (安裝程式), **Linux** (AppImage/DEB/RPM)。

## Python SDK

```bash
pip install anote-ai
```

## TypeScript/JavaScript SDK

```bash
npm install @anote-ai/sdk
```
