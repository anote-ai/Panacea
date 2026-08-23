# 提示库

复制粘贴用于 `anote ask`、`anote chat` 和 `anote fix` 的提示，按任务组织。

## 理解代码

```bash
anote ask "这个代码库的高层次功能是什么？"
anote ask --file src/payments/webhook.ts "逐行带我浏览这个文件"
anote ask "速率限制器在哪里配置，限制是什么？"
anote ask "如果我移除这里的缓存层，会有什么问题？"
```

## 调试

```bash
anote fix --error "$(cat error.log)"
anote ask "为什么这个测试偶尔失败但不一致？"
anote fix src/db/pool.ts "连接没有被释放回池中"
```

## 代码审查

```bash
anote review --file src/auth/session.ts
anote review --pr 42
anote diff --staged -c "关注错误处理和边缘情况"
```

## 重构

```bash
anote refactor src/utils.ts "将其拆分为更小的单一目的函数" --dry-run
anote ask "有没有更简单的方法来表达这个逻辑？" --file src/parser.ts
anote migrate --from "moment" --to "date-fns"
```

## 编写测试

```bash
anote test src/utils/validate.ts --coverage --write
anote ask "这个函数我遗漏了哪些边缘情况？" --file src/utils/validate.ts
```

## 安全性和性能

```bash
anote security --severity high
anote perf --focus "数据库, 包大小"
```

## 文档

```bash
anote docs src/api/client.ts --style jsdoc
anote changelog --since v1.2.0
anote explain --stdout                       # 快速架构摘要
```

## 下一步

- [常见工作流程](common-workflows.md)
- [CLI 命令](../cli/commands.md)
