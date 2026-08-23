# CLI設定

Anote CLIは、プロジェクトのルートにある`.anote.json`またはグローバルに`~/.anote/config.json`を介して構成できます。

## 設定ファイル

```json
{
  "model": "claude-sonnet-4-6",
  "permissionMode": "default",
  "maxTurns": 20,
  "provider": "anthropic"
}
```

## 設定の管理

```bash
anote config list          # すべての設定を表示
anote config get model     # 値を取得
anote config set model claude-haiku-4-5-20251001  # 値を設定
anote config unset model   # 値を削除
```
