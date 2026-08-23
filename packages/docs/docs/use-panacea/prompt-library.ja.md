# プロンプトライブラリ

`anote ask`、`anote chat`、および `anote fix` のプロンプトをタスク別に整理してコピー＆ペーストします。

## コードの理解

```bash
anote ask "このコードベースは高レベルで何をするのか？"
anote ask --file src/payments/webhook.ts "このファイルを行ごとに説明して"
anote ask "レートリミッターはどこで設定されていて、制限は何ですか？"
anote ask "ここでキャッシングレイヤーを削除したら何が壊れますか？"
```

## デバッグ

```bash
anote fix --error "$(cat error.log)"
anote ask "なぜこのテストは時々失敗するのか、一貫していないのか？"
anote fix src/db/pool.ts "接続がプールに戻されていない"
```

## コードレビュー

```bash
anote review --file src/auth/session.ts
anote review --pr 42
anote diff --staged -c "エラーハンドリングとエッジケースに焦点を当てる"
```

## リファクタリング

```bash
anote refactor src/utils.ts "これをより小さく、単一目的の関数に分割する" --dry-run
anote ask "このロジックを表現する簡単な方法はありますか？" --file src/parser.ts
anote migrate --from "moment" --to "date-fns"
```

## テストの作成

```bash
anote test src/utils/validate.ts --coverage --write
anote ask "この関数に対して見落としているエッジケースは何ですか？" --file src/utils/validate.ts
```

## セキュリティとパフォーマンス

```bash
anote security --severity high
anote perf --focus "データベース, バンドルサイズ"
```

## ドキュメント

```bash
anote docs src/api/client.ts --style jsdoc
anote changelog --since v1.2.0
anote explain --stdout                       # 簡単なアーキテクチャの概要
```

## 次のステップ

- [一般的なワークフロー](common-workflows.md)
- [CLIコマンド](../cli/commands.md)
