# CLI コマンド

## `anote ask`

コードに関する質問をします。

```bash
anote ask "認証ミドルウェアはどのように機能しますか？"
anote ask --file src/auth.ts "このファイルを説明してください"
anote ask --compare  # 複数のモデル間で並べて比較
cat file.py | anote ask "バグを見つける"
```

## `anote fix`

現在のディレクトリのバグを修正します。

```bash
anote fix
anote fix --loop                    # テストがパスするまで繰り返す
anote fix --max-iterations 5        # 繰り返し回数を制限
anote fix --file src/broken.ts      # 特定のファイルを修正
```

## `anote review`

バグ、セキュリティ問題、品質のためにコードをレビューします。

```bash
anote review                        # 現在のディレクトリをレビュー
anote review --file src/handler.ts  # 特定のファイルをレビュー
anote review --pr 42                # GitHub PR に AI レビューを投稿
```

## `anote index`

コードベースの TF-IDF セマンティック検索インデックスを構築します。

```bash
anote index              # 現在のディレクトリをインデックス
anote index --watch      # 変更を監視し、再インデックス
anote index /path/to/dir # 特定のディレクトリをインデックス
```

## `anote search`

インデックスされたコードベースをセマンティックに検索します。

```bash
anote search "JWT トークンの検証"
anote search "データベース接続" --top 10
anote search "auth ミドルウェア" --json
```

## `anote doctor`

設定の問題を確認します。

```bash
anote doctor
```

チェック: Node.js ≥ 18, `ANTHROPIC_API_KEY` が設定されている, `.anote.json` が存在する, `CLAW.md` が存在する, git がインストールされている。

## `anote changelog`

git 履歴から CHANGELOG.md エントリを生成します。

```bash
anote changelog
anote changelog --since v1.2.0
anote changelog --dry-run
```

## `anote docs`

未文書化のコードのためのドキュメントを生成します。

```bash
anote docs
anote docs src/api.ts
anote docs --style jsdoc
anote docs --dry-run
```

## `anote migrate`

AI 支援によるコードベースの移行。

```bash
anote migrate --from "React 17" --to "React 18"
anote migrate --from "axios" --to "fetch"
anote migrate --dry-run
```

## `anote security`

コードベースのセキュリティ監査 (OWASP Top 10)。

```bash
anote security
anote security --severity high
anote security --fix
```

## `anote perf`

パフォーマンス分析。

```bash
anote perf
anote perf --focus "database,bundle"
anote perf --fix
```
