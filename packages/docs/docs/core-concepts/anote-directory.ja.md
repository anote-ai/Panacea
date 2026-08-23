# .anote ディレクトリを探る

PanaceaのCLIは、プロジェクトごとのファイルとグローバルなファイルの2つの場所から設定を読み取ります。

## プロジェクト設定

Panaceaは、現在のディレクトリから上に向かって最初に見つけたファイルをこの順序で検索します：

- `.anote.json`
- `.claw.json`
- `anote.config.json`

```json
{
  "model": "claude-sonnet-4-6",
  "permissionMode": "default",
  "maxTurns": 20,
  "compactAfterMessages": 40,
  "hooks": {
    "preToolUse": [],
    "postToolUse": []
  }
}
```

| キー | 目的 |
|---|---|
| `model` | このプロジェクトのデフォルトモデル |
| `permissionMode` | `default`, `acceptEdits`, または `bypassPermissions` — [権限モード](../use-panacea/permission-modes.md)を参照 |
| `provider` | 明示的なプロバイダーのオーバーライド（通常は `model` から自動検出される） |
| `baseUrl` | OpenAI互換エンドポイントのベースURL、例：Ollama用の `http://localhost:11434/v1` |
| `maxTurns` | セッションごとのターン上限 |
| `compactAfterMessages` | セッション履歴をコンパクトにするタイミング |
| `hooks` | `preToolUse` / `postToolUse` シェルフック — [Panaceaを拡張する](extend.md)を参照 |

`anote init` はあなたのために `.anote.json` を作成します。 `anote config` はそれを読み書きします：

```bash
anote config              # 有効な設定を表示（グローバル + ローカル）
anote config get model
anote config set model gpt-4.1
anote config path         # グローバル設定ファイルのパスを表示
anote config edit         # $EDITORでグローバル設定を開く
```

## グローバル設定

`~/.anote/config.json` はあなたのデフォルト設定を保持します — プロジェクトがそれをオーバーライドしない限り適用されます。プロジェクト設定は常にグローバル設定に勝ります。

## CLAW.md

JSONではありません — エージェントが各セッションの開始時にプロジェクトのコンテキストのために読むマークダウンファイルです。何を入れるかは [Panaceaを拡張する](extend.md) を参照してください。

## 次のステップ

- [権限モード](../use-panacea/permission-modes.md)
- [セッションの管理](../use-panacea/sessions.md)
