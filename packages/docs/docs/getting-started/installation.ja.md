# インストール

## CLI

```bash
npm install -g @anote-ai/anote
```

Node.js 18 以降が必要です。

## VS Code 拡張機能

VS Code 拡張機能マーケットプレイスで **"Anote"** を検索するか、次のコマンドでインストールします：

```bash
code --install-extension anote-ai.anote-ai-coding
```

## ウェブアプリ (セルフホスティング)

```bash
git clone https://github.com/anote-ai/Panacea
cd Panacea
cp packages/backend/.env.example packages/backend/.env
# .env をあなたの API キーで編集します
docker compose up
```

フロントエンド: http://localhost:3000 · バックエンド: http://localhost:5000

## デスクトップアプリ

[GitHub Releases](https://github.com/anote-ai/Panacea/releases) から最新のリリースをダウンロードします。

利用可能なプラットフォーム: **macOS** (DMG)、**Windows** (インストーラー)、**Linux** (AppImage/DEB/RPM)。

## Python SDK

```bash
pip install anote-ai
```

## TypeScript/JavaScript SDK

```bash
npm install @anote-ai/sdk
```
