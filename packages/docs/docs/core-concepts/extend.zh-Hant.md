# 擴充 Panacea

有兩種方式可以自訂 Panacea 在你專案中的行為：用於持久性指示的 **CLAW.md**，以及用於在工具呼叫前後執行自訂指令的 **hooks**。

## CLAW.md — 專案記憶

`CLAW.md` 是 Panacea 用於取得專案背景資訊而讀取的 Markdown 檔案 — 概念上類似於 README，只不過面向的是代理而非人類。`anote init` 會自動產生一份，並預先填入偵測到的技術堆疊與驗證指令（test/lint/build）：

```markdown
# CLAW.md

This file provides guidance to Anote AI when working with code in this repository.

## Project overview

<!-- Describe what this project does -->

## Stack

TypeScript · Next.js

## Verification

Run these before considering a change complete:

  npm test
  npm run lint

## Working agreement

- Read relevant files before making changes
- Run the verification commands after modifying logic
- Keep changes small and focused
- Prefer editing existing files over creating new ones
```

你可以自由編輯它 — 加入架構說明、慣例，或代理一直出錯的地方。Panacea 會在該目錄下每次工作階段開始時讀取此檔案。

## Hooks — 在工具呼叫前後執行自訂指令

Hooks 會在每次工具呼叫之前（`preToolUse`）或之後（`postToolUse`）執行一個 shell 指令，於 `.anote.json` 中設定：

```json
{
  "hooks": {
    "preToolUse": ["./scripts/check-tool-policy.sh"],
    "postToolUse": ["npx prettier --write ."]
  }
}
```

**結束代碼語意：**

| 結束代碼 | 效果 |
|---|---|
| `0` | 允許 — stdout 會被擷取為提示訊息 |
| `2` | 拒絕 — stdout 會被擷取為拒絕原因，並顯示給代理 |
| 其他任意值 | 警告但仍然允許 |

使用 `preToolUse` 在風險指令執行前攔截它們或強制套用政策；使用 `postToolUse` 實現諸如每次編輯後自動格式化之類的功能。

## 下一步

- [瞭解 .anote 目錄](anote-directory.md) — CLAW.md 與設定檔的存放位置
- [權限模式](../use-panacea/permission-modes.md) — 控制代理能做什麼的另一個開關
