# 更新日志

Panacea 目前尚未发布手动维护的更新日志文件 — 真实的发布信息来源于：

- **[GitHub 发布](https://github.com/anote-ai/Panacea/releases)** — CLI、VS Code 扩展和其他软件包的标记发布
- **[提交历史](https://github.com/anote-ai/Panacea/commits/main)** — 每个更改，按顺序排列

## 为您的项目生成一个

CLI 可以从 git 历史中为 *您的* 代码库生成更新日志：

```bash
anote changelog                    # 自上一个标签以来
anote changelog --since v1.2.0
anote changelog --dry-run          # 打印而不是写入 CHANGELOG.md
```

这将写入您项目自己的 `CHANGELOG.md`，而不是 Panacea 的。
