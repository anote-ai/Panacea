# CLI 配置

Anote CLI 可以通過項目根目錄中的 `.anote.json` 或全局的 `~/.anote/config.json` 進行配置。

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
anote config list          # 顯示所有設置
anote config get model     # 獲取一個值
anote config set model claude-haiku-4-5-20251001  # 設置一個值
anote config unset model   # 移除一個值
```
