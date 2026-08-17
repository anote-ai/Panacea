# Panacea 的運作方式

Panacea 執行一個**代理迴圈**：它讀取你的提示詞、決定要呼叫哪些工具、執行它們、讀取結果，然後重複此過程 — 將其推理過程與修改內容以串流方式回傳給你 — 直到任務完成或達到輪次上限。

## 工具

預設情況下，Panacea 的代理可以呼叫：

| 工具 | 用途 |
|---|---|
| `Read` | 讀取檔案 |
| `Write` | 建立或覆寫檔案 |
| `Edit` | 對檔案進行針對性修改 |
| `Bash` | 執行 shell 指令 |
| `Glob` | 依模式尋找檔案 |
| `Grep` | 搜尋檔案內容 |

某些指令會縮小這個清單 — 例如 `anote review` 和 `anote diff` 只允許 `Read`、`Glob`、`Grep` 和 `Bash`，因為審查作業不應該寫入檔案。

## 輪次與壓縮

每一組工具呼叫/回應算作一輪。代理在達到 `maxTurns`（預設 30，可透過 `anote config set maxTurns <n>` 或 `.anote.json` 設定）後停止。長時間的工作階段會在 `compactAfterMessages`（預設 40）後被壓縮，以保持上下文視窗可控。

## 串流

每個介面 — CLI、VS Code、網頁、桌面版 — 都與相同的後端端點（`POST /api/chat/stream`）通訊，該端點會透過 SSE 即時串流模型的回應與工具活動。你能即時看到檔案讀取、編輯與指令輸出，而不只是最終答案。

## 多供應商支援

代理迴圈並不綁定於單一模型。`anote ask --compare` 會在多個模型上並排執行同一提示詞，大多數指令的 `--model` 參數接受任何已設定的供應商（`claude-sonnet-4-6`、`gpt-4.1`、`gemini-2.5-pro`，或本機的 `ollama/<model>`）。

## 下一步

- [權限模式](../use-panacea/permission-modes.md) — 控制代理在編輯檔案或執行指令前是否需要詢問
- [擴充 Panacea](extend.md) — CLAW.md 與 hooks
- [CLI 指令](../cli/commands.md) — 完整的指令參考
