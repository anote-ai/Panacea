# クイックスタート

## 1. 初期化

```bash
anote init
```

これにより、APIキーと好みのLLMプロバイダーの設定が案内されます。

## 2. 質問する

```bash
# 一般的な質問
anote ask "このコードベースでの認証はどのように機能しますか？"

# ファイルに焦点を当てる
anote ask --file src/auth.ts "これを説明してください"

# コードをパイプする
cat src/handler.py | anote ask "ここで何が問題になる可能性がありますか？"
```

## 3. バグを自動的に修正する

```bash
# 修正してテストが通るまで繰り返す（最大5ラウンド）
anote fix --loop --max-iterations 5
```

## 4. セマンティック検索のためにインデックスを作成する

```bash
# コードベースをインデックス化する（1回実行し、その後更新を維持）
anote index

# セマンティックに検索する
anote search "JWTトークンの検証"
anote search "データベース接続プール"
```

## 5. PRをレビューする

```bash
anote review --pr 42
```

## 6. チェンジログを生成する

```bash
anote changelog --since v1.2.0
```
