# Panacea 的工作原理

Panacea 运行一个 **代理循环**：它读取您的提示，决定调用哪些工具，执行它们，读取结果，并重复 — 将其推理和编辑实时传回给您 — 直到任务完成或达到回合限制。

## 工具

默认情况下，Panacea 的代理可以调用：

| 工具 | 目的 |
|---|---|
| `Read` | 读取文件 |
| `Write` | 创建或覆盖文件 |
| `Edit` | 对文件进行有针对性的更改 |
| `Bash` | 运行 shell 命令 |
| `Glob` | 按模式查找文件 |
| `Grep` | 搜索文件内容 |

某些命令会缩小此列表 — 例如，`anote review` 和 `anote diff` 仅允许 `Read`、`Glob`、`Grep` 和 `Bash`，因为审查不应写入文件。

## 回合和压缩

每个工具调用/响应对计为一个回合。代理在 `maxTurns`（默认 30，可通过 `anote config set maxTurns <n>` 或 `.anote.json` 配置）后停止。长会话在 `compactAfterMessages`（默认 40）后被压缩，以保持上下文窗口的可管理性。

## 流式传输

每个界面 — CLI、VS Code、Web、桌面 — 都与相同的后端端点 (`POST /api/chat/stream`) 通信，该端点在发生时通过 SSE 流式传输模型的响应和工具活动。您可以实时看到文件读取、编辑和命令输出，而不仅仅是最终答案。

## 多提供者

代理循环并不绑定于一个模型。`anote ask --compare` 在多个模型之间并排运行相同的提示，而大多数命令上的 `--model` 接受任何已配置的提供者（`claude-sonnet-4-6`、`gpt-4.1`、`gemini-2.5-pro`，或本地的 `ollama/<model>`）。

## 下一步

- [权限模式](../use-panacea/permission-modes.md) — 控制代理在编辑或运行命令之前是否询问
- [扩展 Panacea](extend.md) — CLAW.md 和钩子
- [CLI 命令](../cli/commands.md) — 完整的命令参考
