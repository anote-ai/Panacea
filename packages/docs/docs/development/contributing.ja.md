# 貢献

## セットアップ

```bash
git clone https://github.com/anote-ai/Panacea
cd Panacea

# Node.js パッケージをインストール
npm install

# Python バックエンドをセットアップ
cd packages/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# あなたのキーで .env を編集

# すべてを開始
cd ../.. 
docker compose up
```

## 開発ワークフロー

1. `main` からフィーチャーブランチを作成
2. 関連する `packages/` ディレクトリで変更を加える
3. テストを実行: `make test`
4. リンターを実行: `make lint`
5. プルリクエストを作成

## テスト

```bash
# すべてのテスト
make test

# バックエンドのみ
make test-backend

# TypeScript のみ
make test-ts
```

## コード標準

### Python (バックエンド)
- **Ruff** を使用したリンティング (`ruff check .`)
- **Mypy** を使用した型チェック (`mypy .`)
- **Pytest** を使用したテスト (≥80% カバレッジ)
- すべての新しい関数に型注釈を付ける

### TypeScript (フロントエンド/CLI/SDK)
- **ESLint** を使用したリンティング
- **Vitest** または **Jest** を使用したテスト
- 厳格な TypeScript (`"strict": true`)

## CI

GitHub Actions はすべてのプッシュで実行されます:
1. バックエンド: ruff → mypy → pytest (80% カバレッジゲート)
2. TypeScript: ビルド → テスト
3. VS Code: 拡張機能をビルド
4. ドキュメント: MkDocs サイトをビルド
