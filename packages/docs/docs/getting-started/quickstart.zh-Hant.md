# 快速開始

## 1. 初始化

```bash
anote init
```

這將引導您設置您的 API 金鑰和首選的 LLM 提供者。

## 2. 提問

```bash
# 一般問題
anote ask "這個程式碼庫中的身份驗證是如何運作的？"

# 專注於一個檔案
anote ask --file src/auth.ts "解釋這個"

# 管道程式碼
cat src/handler.py | anote ask "這裡可能出現什麼問題？"
```

## 3. 自動修復錯誤

```bash
# 修復並迭代直到測試通過（最多 5 輪）
anote fix --loop --max-iterations 5
```

## 4. 建立語意搜尋索引

```bash
# 建立您的程式碼庫索引（運行一次，然後保持更新）
anote index

# 進行語意搜尋
anote search "JWT 權杖驗證"
anote search "資料庫連接池"
```

## 5. 審查 PR

```bash
anote review --pr 42
```

## 6. 生成變更日誌

```bash
anote changelog --since v1.2.0
```
