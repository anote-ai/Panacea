# 變更紀錄

Panacea 尚未發布手動維護的變更紀錄檔案 — 真正的資訊來源為：

- **[GitHub 版本](https://github.com/anote-ai/Panacea/releases)** — CLI、VS Code 擴展及其他套件的標記版本
- **[提交歷史](https://github.com/anote-ai/Panacea/commits/main)** — 每一個變更，按順序排列

## 為你的專案生成一個

CLI 可以從 git 歷史為 *你的* 程式碼庫寫出變更紀錄：

```bash
anote changelog                    # 自上次標籤以來
anote changelog --since v1.2.0
anote changelog --dry-run          # 輸出而不是寫入 CHANGELOG.md
```

這會寫入你專案自己的 `CHANGELOG.md`，而不是 Panacea 的。
