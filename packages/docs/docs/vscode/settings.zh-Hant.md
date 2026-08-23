# VS Code 擴充功能設定

在 VS Code 的設定 UI 或 `settings.json` 中配置擴充功能。

| 設定 | 預設值 | 描述 |
|------|--------|------|
| `anote.model` | `claude-sonnet-4-6` | 預設使用的模型 |
| `anote.apiKey` | `""` | Anthropic API 權杖（或使用環境變數） |
| `anote.permissionMode` | `default` | 工具權限模式：`default`、`auto`、`manual` |
| `anote.showToolUse` | `true` | 在聊天面板中顯示工具調用 |

```json
{
  "anote.model": "claude-sonnet-4-6",
  "anote.permissionMode": "default"
}
```
