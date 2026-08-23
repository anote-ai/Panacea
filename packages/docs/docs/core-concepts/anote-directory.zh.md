# 探索 .anote 目录

Panacea 的 CLI 从两个地方读取配置：每个项目的文件和一个全局文件。

## 项目配置

Panacea 从当前目录向上搜索第一个找到的文件，顺序如下：

- `.anote.json`
- `.claw.json`
- `anote.config.json`

```json
{
  "model": "claude-sonnet-4-6",
  "permissionMode": "default",
  "maxTurns": 20,
  "compactAfterMessages": 40,
  "hooks": {
    "preToolUse": [],
    "postToolUse": []
  }
}
```

| 键 | 目的 |
|---|---|
| `model` | 此项目的默认模型 |
| `permissionMode` | `default`、`acceptEdits` 或 `bypassPermissions` — 参见 [权限模式](../use-panacea/permission-modes.md) |
| `provider` | 显式提供者覆盖（通常从 `model` 自动检测） |
| `baseUrl` | OpenAI 兼容端点的基础 URL，例如 `http://localhost:11434/v1` 用于 Ollama |
| `maxTurns` | 每个会话的回合上限 |
| `compactAfterMessages` | 何时压缩会话历史 |
| `hooks` | `preToolUse` / `postToolUse` shell 钩子 — 参见 [扩展 Panacea](extend.md) |

`anote init` 为您创建 `.anote.json`。`anote config` 读取和写入它：

```bash
anote config              # 显示有效配置（全局 + 本地）
anote config get model
anote config set model gpt-4.1
anote config path         # 打印全局配置文件路径
anote config edit         # 在 $EDITOR 中打开全局配置
```

## 全局配置

`~/.anote/config.json` 保存您的默认值 — 在项目未覆盖时应用。项目配置始终优先于全局配置。

## CLAW.md

不是 JSON — 代理在每个会话开始时读取的 markdown 文件，用于项目上下文。有关内容，请参见 [扩展 Panacea](extend.md)。

## 下一步

- [权限模式](../use-panacea/permission-modes.md)
- [管理会话](../use-panacea/sessions.md)
