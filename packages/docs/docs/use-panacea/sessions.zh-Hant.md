# 管理工作階段

每個 `anote chat` 會話都會作為工作階段本地保存 — 包括其消息、權杖使用情況和工作目錄。

## 列出工作階段

```bash
anote sessions list
anote sessions ls --limit 50
```

```
已保存的工作階段 (3):
  a1b2c3d4  12 條消息  in=4,200 out=1,800  10 分鐘前  /Users/you/project
  e5f6a7b8  4 條消息   in=900 out=400      2 小時前   /Users/you/other-project
```

## 顯示工作階段

```bash
anote sessions show a1b2c3d4
anote sessions show a1b2c3d4 --limit 50   # 更多消息歷史
```

打印該工作階段的對話、權杖總數和工作目錄。您可以傳遞工作階段 ID 的短前綴，而不是完整的 ID。

## 刪除工作階段

```bash
anote sessions delete a1b2c3d4
anote sessions rm a1b2c3d4
```

## 下一步

- [常見工作流程](common-workflows.md)
- [Panacea 如何運作](../core-concepts/how-it-works.md) — 輪次、壓縮，以及工作階段長度如何影響上下文
