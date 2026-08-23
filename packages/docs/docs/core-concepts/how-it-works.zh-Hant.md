# Panacea 的運作方式

Panacea 運行一個 **代理迴圈**：它讀取您的提示，決定要調用哪些工具，執行它們，讀取結果，並重複 — 將其推理和編輯內容串流回您 — 直到任務完成或達到回合限制。

## 工具

默認情況下，Panacea 的代理可以調用：

| 工具 | 目的 |
|---|---|
| `Read` | 讀取文件 |
| `Write` | 創建或覆蓋文件 |
| `Edit` | 對文件進行有針對性的更改 |
| `Bash` | 執行 shell 命令 |
| `Glob` | 按模式查找文件 |
| `Grep` | 搜索文件內容 |

某些命令會縮小此列表 — 例如，`anote review` 和 `anote diff` 只允許 `Read`、`Glob`、`Grep` 和 `Bash`，因為審查不應該寫入文件。

## 回合和壓縮

每個工具調用/響應對都算作一個回合。代理在 `maxTurns`（默認為 30，可通過 `anote config set maxTurns <n>` 或 `.anote.json` 配置）後停止。長會話在 `compactAfterMessages`（默認為 40）後進行壓縮，以保持上下文窗口的可管理性。

## 串流

每個界面 — CLI、VS Code、Web、桌面 — 都與相同的後端端點 (`POST /api/chat/stream`) 進行通訊，該端點在發生時通過 SSE 串流模型的響應和工具活動。您可以實時看到文件讀取、編輯和命令輸出，而不僅僅是最終答案。

## 多提供者

代理迴圈並不僅限於一個模型。`anote ask --compare` 在多個模型之間並排運行相同的提示，而大多數命令上的 `--model` 接受任何配置的提供者（`claude-sonnet-4-6`、`gpt-4.1`、`gemini-2.5-pro`，或本地的 `ollama/<model>`）。

## 下一步

- [權限模式](../use-panacea/permission-modes.md) — 控制代理在編輯或運行命令之前是否詢問
- [擴展 Panacea](extend.md) — CLAW.md 和鉤子
- [CLI 命令](../cli/commands.md) — 完整的命令參考
