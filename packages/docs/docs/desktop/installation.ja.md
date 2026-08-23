# デスクトップアプリのインストール

## ダウンロード

GitHubのリリースページから、あなたのプラットフォームに合った最新のリリースをダウンロードしてください。

| プラットフォーム | ファイル |
|------------------|----------|
| macOS            | `Anote-AI-x.x.x.dmg` |
| Windows          | `Anote-AI-Setup-x.x.x.exe` |
| Linux (deb)     | `anote-ai_x.x.x_amd64.deb` |

## ソースからのビルド

```bash
# 1. Pythonバックエンドをバンドルする
cd packages/backend
pip install pyinstaller
pyinstaller ../desktop/app.spec --distpath ../desktop/backend-dist

# 2. Electronアプリをビルドしてパッケージ化する
cd packages/desktop
npm install
npm run make
```

パッケージ化されたアプリは `packages/desktop/out/` にあります。
