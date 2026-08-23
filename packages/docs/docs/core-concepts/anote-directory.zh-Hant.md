# 探索 .anote 目錄

Panacea 的 CLI 從兩個地方讀取配置：每個專案的文件和全局文件。

## 專案配置

Panacea 從當前目錄向上搜索第一個找到的文件，順序如下：

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

| 鍵 | 目的 |
|---|---|
| `model` | 此專案的預設模型 |
| `permissionMode` | `default`、`acceptEdits` 或 `bypassPermissions` — 參見 [權限模式](../use-panacea/permission-modes.md) |
| `provider` | 明確的提供者覆蓋（通常從 `model` 自動檢測） |
| `baseUrl` | OpenAI 兼容端點的基本 URL，例如 `http://localhost:11434/v1` 用於 Ollama |
| `maxTurns` | 每個工作階段的回合上限 |
| `compactAfterMessages` | 何時壓縮會話歷史 |
| `hooks` | `preToolUse` / `postToolUse` shell 鉤子 — 參見 [擴展 Panacea](extend.md) |

`anote init` 為您創建 `.anote.json`。`anote config` 讀取和寫入它：

```bash
anote config              # 顯示有效配置（全局 + 本地）
anote config get model
anote config set model gpt-4.1
anote config path         # 打印全局配置文件路徑
anote config edit         # 在 $EDITOR 中打開全局配置
```

## 全局配置

`~/.anote/config.json` 保存您的預設值 — 當專案未覆蓋它們時應用。專案配置始終優先於全局配置。

## CLAW.md

不是 JSON — 一個 markdown 文件，代理在每個會話開始時讀取以獲取專案上下文。參見 [擴展 Panacea](extend.md) 了解應該放入其中的內容。

## 下一步

- [權限模式](../use-panacea/permission-modes.md)
- [管理會話](../use-panacea/sessions.md)
