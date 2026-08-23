# CLI 配置

Anote CLI 可以通过项目根目录中的 `.anote.json` 或全局的 `~/.anote/config.json` 进行配置。

## 配置文件

```json
{
  "model": "claude-sonnet-4-6",
  "permissionMode": "default",
  "maxTurns": 20,
  "provider": "anthropic"
}
```

## 管理配置

```bash
anote config list          # 显示所有设置
anote config get model     # 获取一个值
anote config set model claude-haiku-4-5-20251001  # 设置一个值
anote config unset model   # 移除一个值
```
