# CLI 概要

`anote` CLI は、AI アシスタンスを直接ターミナルに提供します。

## インストール

```bash
npm install -g @anote-ai/anote
```

## コアコマンド

| コマンド | 説明 |
|---|---|
| `anote ask <question>` | コードについて質問する |
| `anote fix [--loop]` | AI 支援によるバグ修正 |
| `anote explain` | ファイルまたは選択範囲を説明する |
| `anote review [--pr N]` | コードレビューまたは PR レビュー |
| `anote test` | テストを生成または実行する |
| `anote refactor` | コードをリファクタリングする |
| `anote index` | セマンティック検索インデックスを構築する |
| `anote search <query>` | セマンティックコード検索 |
| `anote commit` | コミットメッセージを生成する |
| `anote changelog` | チェンジログを生成する |
| `anote docs` | ドキュメントを生成する |
| `anote migrate` | AI 支援によるマイグレーション |
| `anote security` | セキュリティ監査 |
| `anote perf` | パフォーマンス分析 |
| `anote doctor` | 環境の健康状態をチェックする |
| `anote init` | Anote をセットアップする |
| `anote config` | 設定を管理する |

完全な使用法については [コマンド](commands.md) を参照してください。
