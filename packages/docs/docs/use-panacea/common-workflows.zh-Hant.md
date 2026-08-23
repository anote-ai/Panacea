# 常見工作流程

逐步模式以處理 Panacea 的 CLI 日常任務。

## 探索不熟悉的程式碼庫

```bash
anote explain                       # 生成 CODEBASE.md 導覽
anote explain src/auth.ts "這是怎麼運作的？"
anote index && anote search "JWT 驗證"
```

`explain` 無參數時會寫入整個倉庫的 `CODEBASE.md` 概述。指向一個檔案或詢問具體問題以深入了解。

## 修復錯誤

```bash
anote fix --error "TypeError: cannot read property 'id' of undefined"
anote fix src/handler.ts "網路鉤子處理器在負載下丟失事件"
anote fix --loop --cmd "npm test"          # 持續迭代直到測試通過
```

## 撰寫並提交

```bash
anote generate "一個用於 Express 的速率限制中介軟體" -o src/middleware/rateLimit.ts
anote test src/middleware/rateLimit.ts --write
anote commit                                # AI 生成的提交訊息
```

## 推送前進行審查

```bash
anote diff --staged                         # 審查已暫存的變更
anote review --pr 42                        # 或審查一個開放的 GitHub PR
anote security --severity high              # OWASP 前十名審核
```

## 開啟拉取請求

```bash
anote pr --gh                               # 生成描述，使用 gh CLI 開啟
```

## 安全重構

```bash
anote refactor src/legacy.ts "將驗證邏輯提取到自己的函數中" --dry-run
anote refactor src/legacy.ts "將驗證邏輯提取到自己的函數中" --auto
```

在任何尚未審查的內容上，始終先嘗試 `--dry-run`。

## 在做其他事情時繼續工作

```bash
anote watch "src/**/*.ts"                   # 每次保存時重新分析
```

## 隨時記錄文件

```bash
anote docs src/api.ts --style jsdoc
anote changelog --since v1.2.0
```

## 下一步

- [提示庫](prompt-library.md) — 複製粘貼起始點
- [CLI 命令](../cli/commands.md) — 完整的標誌參考
