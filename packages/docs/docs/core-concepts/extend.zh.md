# 扩展 Panacea

有两种方式可以自定义 Panacea 在你项目中的行为：用于持久性指令的 **CLAW.md**，以及用于在工具调用前后运行自定义命令的**钩子（hooks）**。

## CLAW.md — 项目记忆

`CLAW.md` 是 Panacea 用于获取项目上下文而读取的 Markdown 文件 — 概念上类似于 README，只不过面向的是智能体而非人类。`anote init` 会自动生成一个，并预先填入检测到的技术栈和验证命令（test/lint/build）：

```markdown
# CLAW.md

This file provides guidance to Anote AI when working with code in this repository.

## Project overview

<!-- Describe what this project does -->

## Stack

TypeScript · Next.js

## Verification

Run these before considering a change complete:

  npm test
  npm run lint

## Working agreement

- Read relevant files before making changes
- Run the verification commands after modifying logic
- Keep changes small and focused
- Prefer editing existing files over creating new ones
```

你可以自由编辑它 — 添加架构说明、约定，或智能体一直出错的地方。Panacea 会在该目录下每次会话开始时读取此文件。

## 钩子 — 在工具调用前后运行自定义命令

钩子会在每次工具调用之前（`preToolUse`）或之后（`postToolUse`）运行一个 shell 命令，在 `.anote.json` 中配置：

```json
{
  "hooks": {
    "preToolUse": ["./scripts/check-tool-policy.sh"],
    "postToolUse": ["npx prettier --write ."]
  }
}
```

**退出码语义：**

| 退出码 | 效果 |
|---|---|
| `0` | 允许 — stdout 会被捕获为提示信息 |
| `2` | 拒绝 — stdout 会被捕获为拒绝原因，并展示给智能体 |
| 其他任意值 | 警告但仍然允许 |

使用 `preToolUse` 在风险命令执行前拦截它们或强制执行策略；使用 `postToolUse` 实现诸如每次编辑后自动格式化之类的功能。

## 下一步

- [了解 .anote 目录](anote-directory.md) — CLAW.md 和配置文件的存放位置
- [权限模式](../use-panacea/permission-modes.md) — 控制智能体能做什么的另一个开关
