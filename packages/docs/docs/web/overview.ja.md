# ウェブアプリの概要

Anote AI ウェブアプリは、Anote バックエンドに接続する ChatGPT スタイルのチャットインターフェースです。

## 機能

- ライトモードとダークモード（システムの設定を自動検出）
- SSE を介したストリーミングレスポンス
- 折りたたみ可能なサイドバーにチャットセッションの履歴
- モデルセレクター（Claude, GPT-4o など）
- ドキュメントのアップロードと Q&A
- レスポンシブデザイン

## ローカルでの実行

```bash
cd packages/web
npm install
npm run dev
```

アプリは `http://localhost:3000` で実行され、API コールは `http://localhost:5000` にプロキシされます。
