# 擴展 Panacea

有兩種方法可以自訂 Panacea 在您的專案中的行為：**CLAW.md** 用於持久指令，以及 **hooks** 用於在工具調用周圍運行您自己的命令。

## CLAW.md — 專案記憶

`CLAW.md` 是一個 Panacea 讀取的 markdown 檔案，用於專案上下文 — 與針對人類的 README 相同的概念，但針對代理。`anote init` 自動生成一個，預填充您的檢測堆疊和驗證命令（測試/檢查/構建）：

```markdown
# CLAW.md

此檔案在處理此程式碼庫中的程式碼時為 Anote AI 提供指導。

## 專案概述

<!-- 描述此專案的功能 -->

## 堆疊

TypeScript · Next.js

## 驗證

在考慮變更完成之前運行這些命令：

  npm test
  npm run lint

## 工作協議

- 在進行更改之前閱讀相關檔案
- 修改邏輯後運行驗證命令
- 保持更改小而專注
- 優先編輯現有檔案而非創建新檔案
```

隨意編輯 — 添加架構筆記、約定或代理經常出錯的事項。Panacea 在每個工作階段開始時會在該目錄中讀取它。

## Hooks — 在工具調用周圍運行您自己的命令

Hooks 在每次工具調用之前（`preToolUse`）或之後（`postToolUse`）運行一個 shell 命令，配置在 `.anote.json` 中：

```json
{
  "hooks": {
    "preToolUse": ["./scripts/check-tool-policy.sh"],
    "postToolUse": ["npx prettier --write ."]
  }
}
```

**退出代碼語義：**

| 退出代碼 | 效果 |
|---|---|
| `0` | 允許 — 標準輸出被捕獲為資訊性消息 |
| `2` | 拒絕 — 標準輸出被捕獲為原因，顯示給代理 |
| 其他任何值 | 警告但允許 |

使用 `preToolUse` 來阻止風險命令或在它們運行之前強制執行政策；使用 `postToolUse` 來進行自動格式化等操作，在每次編輯後執行。

## 下一步

- [探索 .anote 目錄](anote-directory.md) — CLAW.md 和配置所在的位置
- [權限模式](../use-panacea/permission-modes.md) — 代理可以做的另一個槓桿
