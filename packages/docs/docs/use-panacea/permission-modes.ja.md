# 権限モード

Panacea には、エージェントがファイルを書き込んだりコマンドを実行する前に確認するかどうかを制御する3つの権限モードがあります。

| モード | 動作 |
|---|---|
| `default` | ファイルを編集したり、読み取り専用でないコマンドを実行する前に確認します |
| `acceptEdits` | 質問せずにファイルの編集を自動的に受け入れます |
| `bypassPermissions` | 確認なしで全てを実行します — 注意して使用してください |

グローバルまたはプロジェクトごとに設定できます：

```bash
anote config set permissionMode acceptEdits
```

または `.anote.json` にて：

```json
{ "permissionMode": "acceptEdits" }
```

## コマンドごとのオーバーライド

ほとんどのコマンドはグローバル設定を触る必要はありません — 同じアイデアのために独自のフラグを取ります：

| フラグ | 使用可能なコマンド | 効果 |
|---|---|---|
| `--auto` | `fix`, `refactor` | この実行のためだけに編集を自動的に受け入れます |
| `--dry-run` | `fix`, `docs`, `migrate`, `security`, `perf`, `refactor`, `generate`, `changelog`, `commit`, `review` | 何も書き込まずに何が起こるかを表示します |
| `--no-edit` | `ask` | 読み取り専用 — エージェントはファイルを変更できません |
| `--yes` | `init` | インタラクティブなプロンプトをスキップし、デフォルトを受け入れます |

`anote fix --loop` は自動的に `acceptEdits` を暗示します。なぜなら、各イテレーションで確認することなく編集を続ける必要があるからです。

## ポリシーレイヤーとしてのフック

「尋ねる vs. 尋ねない」よりも具体的なこと — 特定のパスに触れる `Bash` コールをブロックするような — には、代わりに `preToolUse` フックを使用してください。詳細は [Panaceaの拡張](../core-concepts/extend.md) を参照してください。

## 次のステップ

- [Panaceaの動作](../core-concepts/how-it-works.md) — これらのモードが制御するエージェントループ
- [ .anote ディレクトリを探る](../core-concepts/anote-directory.md) — `permissionMode` が設定に存在する場所
