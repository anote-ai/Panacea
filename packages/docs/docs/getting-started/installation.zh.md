# 安装

## CLI

```bash
npm install -g @anote-ai/anote
```

需要 Node.js 18 或更高版本。

## VS Code 扩展

在 VS Code 扩展市场中搜索 **"Anote"**，或通过以下方式安装：

```bash
code --install-extension anote-ai.anote-ai-coding
```

## Web 应用程序（自托管）

```bash
git clone https://github.com/anote-ai/Panacea
cd Panacea
cp packages/backend/.env.example packages/backend/.env
# 使用您的 API 密钥编辑 .env
docker compose up
```

前端: http://localhost:3000 · 后端: http://localhost:5000

## 桌面应用程序

从 [GitHub Releases](https://github.com/anote-ai/Panacea/releases) 下载最新版本。

适用于: **macOS** (DMG), **Windows** (安装程序), **Linux** (AppImage/DEB/RPM)。

## Python SDK

```bash
pip install anote-ai
```

## TypeScript/JavaScript SDK

```bash
npm install @anote-ai/sdk
```
