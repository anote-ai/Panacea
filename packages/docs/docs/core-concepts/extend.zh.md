# 扩展 Panacea

有两种方法可以自定义 Panacea 在您的项目中的行为：**CLAW.md** 用于持久指令，以及 **hooks** 用于在工具调用周围运行您自己的命令。

## CLAW.md — 项目记忆

`CLAW.md` 是一个 markdown 文件，Panacea 用于读取项目上下文 — 这个想法与面向代理的 README 相同，而不是面向人类。`anote init` 会自动生成一个，预填充您检测到的堆栈和验证命令（测试/代码检查/构建）：

```markdown
# CLAW.md

此文件为 Anote AI 在处理此代码库中的代码时提供指导。

## 项目概述

<!-- 描述此项目的功能 -->

## 堆栈

TypeScript · Next.js

## 验证

在考虑更改完成之前运行这些命令：

  npm test
  npm run lint

## 工作协议

- 在进行更改之前阅读相关文件
- 修改逻辑后运行验证命令
- 保持更改小而集中
- 优先编辑现有文件而不是创建新文件
```

可以自由编辑 — 添加架构说明、约定或代理经常出错的内容。Panacea 在每次会话开始时都会读取它。

## Hooks — 在工具调用周围运行您自己的命令

Hooks 在每次工具调用之前（`preToolUse`）或之后（`postToolUse`）运行一个 shell 命令，配置在 `.anote.json` 中：

```json
{
  "hooks": {
    "preToolUse": ["./scripts/check-tool-policy.sh"],
    "postToolUse": ["npx prettier --write ."]
  }
}
```

**退出代码语义：**

| 退出代码 | 效果 |
|---|---|
| `0` | 允许 — 标准输出被捕获为信息消息 |
| `2` | 拒绝 — 标准输出被捕获为原因，显示给代理 |
| 其他 | 警告但允许 |

使用 `preToolUse` 阻止风险命令或在它们运行之前强制执行策略；使用 `postToolUse` 进行每次编辑后的自动格式化等操作。

## 下一步

- [探索 .anote 目录](anote-directory.md) — CLAW.md 和配置所在的位置
- [权限模式](../use-panacea/permission-modes.md) — 代理可以做的另一种杠杆
