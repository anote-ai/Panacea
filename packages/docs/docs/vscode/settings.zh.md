# VS Code 扩展设置

在 VS Code 的设置 UI 或 `settings.json` 中配置扩展。

| 设置 | 默认值 | 描述 |
|------|--------|------|
| `anote.model` | `claude-sonnet-4-6` | 默认使用的模型 |
| `anote.apiKey` | `""` | Anthropic API 密钥（或使用环境变量） |
| `anote.permissionMode` | `default` | 工具权限模式：`default`、`auto`、`manual` |
| `anote.showToolUse` | `true` | 在聊天面板中显示工具调用 |

```json
{
  "anote.model": "claude-sonnet-4-6",
  "anote.permissionMode": "default"
}
```
