# 常见工作流程

Panacea CLI 的日常任务逐步模式。

## 探索不熟悉的代码库

```bash
anote explain                       # 生成 CODEBASE.md 导览
anote explain src/auth.ts "这如何工作？"
anote index && anote search "JWT 验证"
```

`explain` 不带参数时，会写入整个代码库的 `CODEBASE.md` 概述。将其指向一个文件或询问具体问题以深入了解。

## 修复错误

```bash
anote fix --error "TypeError: cannot read property 'id' of undefined"
anote fix src/handler.ts "webhook 处理程序在负载下丢弃事件"
anote fix --loop --cmd "npm test"          # 持续迭代直到测试通过
```

## 编写并提交

```bash
anote generate "一个用于 Express 的速率限制中间件" -o src/middleware/rateLimit.ts
anote test src/middleware/rateLimit.ts --write
anote commit                                # AI 生成的提交信息
```

## 在推送之前进行审查

```bash
anote diff --staged                         # 审查已暂存的更改
anote review --pr 42                        # 或审查一个开放的 GitHub PR
anote security --severity high              # OWASP 前 10 名审计
```

## 打开拉取请求

```bash
anote pr --gh                               # 生成描述，使用 gh CLI 打开
```

## 安全重构

```bash
anote refactor src/legacy.ts "将验证逻辑提取到自己的函数中" --dry-run
anote refactor src/legacy.ts "将验证逻辑提取到自己的函数中" --auto
```

在任何尚未审查的内容上，始终先尝试 `--dry-run`。

## 在做其他事情时继续工作

```bash
anote watch "src/**/*.ts"                   # 每次保存时重新分析
```

## 边做边记录文档

```bash
anote docs src/api.ts --style jsdoc
anote changelog --since v1.2.0
```

## 下一步

- [提示库](prompt-library.md) — 复制粘贴起始点
- [CLI 命令](../cli/commands.md) — 完整标志参考
