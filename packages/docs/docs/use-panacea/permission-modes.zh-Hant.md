# 權限模式

Panacea 有三種權限模式，控制代理在寫入檔案或執行命令之前是否詢問。

| 模式 | 行為 |
|---|---|
| `default` | 在編輯檔案或執行非唯讀命令之前確認 |
| `acceptEdits` | 自動接受檔案編輯而不詢問 |
| `bypassPermissions` | 在不確認的情況下執行所有操作 — 請小心使用 |

全域或每個專案設定：

```bash
anote config set permissionMode acceptEdits
```

或在 `.anote.json` 中：

```json
{ "permissionMode": "acceptEdits" }
```

## 每個命令的覆蓋

大多數命令不需要您觸及全域配置 — 它們有自己的標誌來實現相同的概念：

| 標誌 | 可用於 | 效果 |
|---|---|---|
| `--auto` | `fix`, `refactor` | 僅對這次運行自動接受編輯 |
| `--dry-run` | `fix`, `docs`, `migrate`, `security`, `perf`, `refactor`, `generate`, `changelog`, `commit`, `review` | 顯示不寫入任何內容的情況下會發生什麼 |
| `--no-edit` | `ask` | 唯讀 — 代理即使想也無法修改檔案 |
| `--yes` | `init` | 跳過互動提示，接受預設值 |

`anote fix --loop` 自動隱含 `acceptEdits`，因為它需要在迭代過程中持續編輯，而不必每次都停下來詢問。

## 作為政策層的鉤子

對於比「詢問與不詢問」更具體的情況 — 例如阻止觸及特定路徑的 `Bash` 調用 — 請改用 `preToolUse` 鉤子。請參見 [擴展 Panacea](../core-concepts/extend.md)。

## 下一步

- [Panacea 的運作方式](../core-concepts/how-it-works.md) — 這些模式控制的代理循環
- [探索 .anote 目錄](../core-concepts/anote-directory.md) — `permissionMode` 在配置中的位置
