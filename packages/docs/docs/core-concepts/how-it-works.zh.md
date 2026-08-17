# Panacea 的工作原理

Panacea 运行一个**智能体循环**：它读取你的提示词，决定调用哪些工具，执行它们，读取结果，然后重复此过程 — 将其推理过程和修改内容以流式方式返回给你 — 直到任务完成或达到轮次上限。

## 工具

默认情况下，Panacea 的智能体可以调用：

| 工具 | 用途 |
|---|---|
| `Read` | 读取文件 |
| `Write` | 创建或覆盖文件 |
| `Edit` | 对文件进行有针对性的修改 |
| `Bash` | 运行 shell 命令 |
| `Glob` | 按模式查找文件 |
| `Grep` | 搜索文件内容 |

某些命令会缩小这个列表 — 例如 `anote review` 和 `anote diff` 只允许 `Read`、`Glob`、`Grep` 和 `Bash`，因为审查操作不应该写入文件。

## 轮次与压缩

每一对工具调用/响应算作一轮。智能体在达到 `maxTurns`（默认 30，可通过 `anote config set maxTurns <n>` 或 `.anote.json` 配置）后停止。长会话会在 `compactAfterMessages`（默认 40）后被压缩，以保持上下文窗口可控。

## 流式传输

每个界面 — CLI、VS Code、网页、桌面端 — 都与同一个后端端点（`POST /api/chat/stream`）通信，该端点通过 SSE 实时流式传输模型的响应和工具活动。你可以实时看到文件读取、编辑和命令输出，而不仅仅是最终答案。

## 多提供商支持

智能体循环并不绑定于单一模型。`anote ask --compare` 会在多个模型上并排运行同一提示词，大多数命令的 `--model` 参数接受任何已配置的提供商（`claude-sonnet-4-6`、`gpt-4.1`、`gemini-2.5-pro`，或本地的 `ollama/<model>`）。

## 下一步

- [权限模式](../use-panacea/permission-modes.md) — 控制智能体在编辑文件或执行命令前是否需要询问
- [扩展 Panacea](extend.md) — CLAW.md 与钩子
- [CLI 命令](../cli/commands.md) — 完整的命令参考
