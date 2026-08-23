# 管理会话

每个 `anote chat` 对话都作为会话保存在本地——包括其消息、令牌使用情况和工作目录。

## 列出会话

```bash
anote sessions list
anote sessions ls --limit 50
```

```
保存的会话 (3):
  a1b2c3d4  12 条消息  in=4,200 out=1,800  10分钟前  /Users/you/project
  e5f6a7b8  4 条消息   in=900 out=400      2小时前   /Users/you/other-project
```

## 显示会话

```bash
anote sessions show a1b2c3d4
anote sessions show a1b2c3d4 --limit 50   # 更多消息历史
```

打印该会话的对话、令牌总数和工作目录。您可以传递会话 ID 的短前缀，而不是完整的 ID。

## 删除会话

```bash
anote sessions delete a1b2c3d4
anote sessions rm a1b2c3d4
```

## 下一步

- [常见工作流程](common-workflows.md)
- [Panacea 的工作原理](../core-concepts/how-it-works.md) — 回合、压缩，以及会话长度如何影响上下文
