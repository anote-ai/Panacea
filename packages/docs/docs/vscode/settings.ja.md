# VS Code 拡張機能の設定

VS Code の設定 UI または `settings.json` で拡張機能を構成します。

| 設定 | デフォルト | 説明 |
|------|------------|------|
| `anote.model` | `claude-sonnet-4-6` | 使用するデフォルトモデル |
| `anote.apiKey` | `""` | Anthropic API キー（または環境変数を使用） |
| `anote.permissionMode` | `default` | ツールの権限モード: `default`, `auto`, `manual` |
| `anote.showToolUse` | `true` | チャットパネルにツールの呼び出しを表示 |

```json
{
  "anote.model": "claude-sonnet-4-6",
  "anote.permissionMode": "default"
}
```
