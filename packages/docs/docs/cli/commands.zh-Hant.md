# CLI 命令

## `anote ask`

詢問有關您程式碼的任何問題。

```bash
anote ask "身份驗證中介軟體如何運作？"
anote ask --file src/auth.ts "解釋這個檔案"
anote ask --compare  # 在多個模型之間並排顯示
cat file.py | anote ask "找出錯誤"
```

## `anote fix`

修復當前目錄中的錯誤。

```bash
anote fix
anote fix --loop                    # 迭代直到測試通過
anote fix --max-iterations 5        # 限制迭代次數
anote fix --file src/broken.ts      # 修復特定檔案
```

## `anote review`

檢查程式碼中的錯誤、安全問題和質量。

```bash
anote review                        # 檢查當前目錄
anote review --file src/handler.ts  # 檢查特定檔案
anote review --pr 42                # 在 GitHub PR 上發佈 AI 審查
```

## `anote index`

建立您程式碼庫的 TF-IDF 語意搜尋索引。

```bash
anote index              # 索引當前目錄
anote index --watch      # 監視變更並重新索引
anote index /path/to/dir # 索引特定目錄
```

## `anote search`

以語意方式搜尋您的索引程式碼庫。

```bash
anote search "JWT 權杖驗證"
anote search "資料庫連接" --top 10
anote search "身份驗證中介軟體" --json
```

## `anote doctor`

檢查您的環境是否存在配置問題。

```bash
anote doctor
```

檢查項目：Node.js ≥ 18，設定 `ANTHROPIC_API_KEY`，存在 `.anote.json`，存在 `CLAW.md`，已安裝 git。

## `anote changelog`

從 git 歷史生成 CHANGELOG.md 條目。

```bash
anote changelog
anote changelog --since v1.2.0
anote changelog --dry-run
```

## `anote docs`

為未記錄的程式碼生成文檔。

```bash
anote docs
anote docs src/api.ts
anote docs --style jsdoc
anote docs --dry-run
```

## `anote migrate`

AI 輔助的程式碼庫遷移。

```bash
anote migrate --from "React 17" --to "React 18"
anote migrate --from "axios" --to "fetch"
anote migrate --dry-run
```

## `anote security`

對您的程式碼庫進行安全審核（OWASP 前 10 名）。

```bash
anote security
anote security --severity high
anote security --fix
```

## `anote perf`

性能分析。

```bash
anote perf
anote perf --focus "database,bundle"
anote perf --fix
```
