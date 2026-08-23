# 提示庫

複製並粘貼 `anote ask`、`anote chat` 和 `anote fix` 的提示，按任務組織。

## 理解程式碼

```bash
anote ask "這個程式碼庫的高層次功能是什麼？"
anote ask --file src/payments/webhook.ts "逐行帶我瀏覽這個檔案"
anote ask "速率限制器配置在哪裡，限制是什麼？"
anote ask "如果我移除這裡的快取層，會破壞什麼？"
```

## 除錯

```bash
anote fix --error "$(cat error.log)"
anote ask "為什麼這個測試會間歇性失敗但不會持續失敗？"
anote fix src/db/pool.ts "連接沒有被釋放回池中"
```

## 程式碼審查

```bash
anote review --file src/auth/session.ts
anote review --pr 42
anote diff --staged -c "專注於錯誤處理和邊界情況"
```

## 重構

```bash
anote refactor src/utils.ts "將這個拆分為更小的單一用途函數" --dry-run
anote ask "有沒有更簡單的方法來表達這個邏輯？" --file src/parser.ts
anote migrate --from "moment" --to "date-fns"
```

## 撰寫測試

```bash
anote test src/utils/validate.ts --coverage --write
anote ask "這個函數我漏掉了哪些邊界情況？" --file src/utils/validate.ts
```

## 安全性和性能

```bash
anote security --severity high
anote perf --focus "資料庫, 包大小"
```

## 文件

```bash
anote docs src/api/client.ts --style jsdoc
anote changelog --since v1.2.0
anote explain --stdout                       # 快速架構摘要
```

## 下一步

- [常見工作流程](common-workflows.md)
- [CLI 命令](../cli/commands.md)
