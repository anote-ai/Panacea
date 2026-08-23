# 一般的なワークフロー

PanaceaのCLIを使用した日常的なタスクのステップバイステップのパターン。

## 不慣れなコードベースを探索する

```bash
anote explain                       # CODEBASE.mdツアーを生成
anote explain src/auth.ts "これはどう機能しますか？"
anote index && anote search "JWT validation"
```

引数なしの`explain`は、リポジトリ全体の`CODEBASE.md`の概要を記述します。ファイルを指定するか、特定の質問をして詳細を掘り下げます。

## バグを修正する

```bash
anote fix --error "TypeError: cannot read property 'id' of undefined"
anote fix src/handler.ts "ウェブフックハンドラーが負荷の下でイベントをドロップします"
anote fix --loop --cmd "npm test"          # テストが通るまで繰り返し実行
```

## コードを書くとコミットする

```bash
anote generate "Express用のレートリミッターミドルウェア" -o src/middleware/rateLimit.ts
anote test src/middleware/rateLimit.ts --write
anote commit                                # AI生成のコミットメッセージ
```

## プッシュする前にレビューする

```bash
anote diff --staged                         # ステージされた変更をレビュー
anote review --pr 42                        # またはオープンなGitHub PRをレビュー
anote security --severity high              # OWASP Top 10監査
```

## プルリクエストを開く

```bash
anote pr --gh                               # 説明を生成し、gh CLIで開く
```

## 安全にリファクタリングする

```bash
anote refactor src/legacy.ts "検証ロジックを独自の関数に抽出する" --dry-run
anote refactor src/legacy.ts "検証ロジックを独自の関数に抽出する" --auto
```

まだレビューしていないものには、まず`--dry-run`を試してください。

## 他の作業をしながら作業を続ける

```bash
anote watch "src/**/*.ts"                   # 保存のたびに再分析
```

## 進めながら文書化する

```bash
anote docs src/api.ts --style jsdoc
anote changelog --since v1.2.0
```

## 次のステップ

- [プロンプトライブラリ](prompt-library.md) — コピー＆ペーストの出発点
- [CLIコマンド](../cli/commands.md) — 完全なフラグリファレンス
