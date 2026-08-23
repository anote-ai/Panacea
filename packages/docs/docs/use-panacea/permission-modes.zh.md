# 权限模式

Panacea 有三种权限模式，控制代理在写入文件或运行命令之前是否询问。

| 模式 | 行为 |
|---|---|
| `default` | 在编辑文件或运行非只读命令之前进行确认 |
| `acceptEdits` | 自动接受文件编辑，无需询问 |
| `bypassPermissions` | 无需确认地运行所有操作 — 请谨慎使用 |

可以全局设置或按项目设置：

```bash
anote config set permissionMode acceptEdits
```

或在 `.anote.json` 中：

```json
{ "permissionMode": "acceptEdits" }
```

## 每个命令的覆盖

大多数命令不需要您触及全局配置 — 它们为相同的想法提供自己的标志：

| 标志 | 可用命令 | 效果 |
|---|---|---|
| `--auto` | `fix`, `refactor` | 仅在此运行中自动接受编辑 |
| `--dry-run` | `fix`, `docs`, `migrate`, `security`, `perf`, `refactor`, `generate`, `changelog`, `commit`, `review` | 显示在不写入任何内容的情况下会发生什么 |
| `--no-edit` | `ask` | 只读 — 即使代理想要也无法修改文件 |
| `--yes` | `init` | 跳过交互式提示，接受默认值 |

`anote fix --loop` 自动隐含 `acceptEdits`，因为它需要在迭代中持续编辑，而不需要每次都停下来询问。

## 钩子作为策略层

对于比“询问与不询问”更具体的情况 — 例如阻止触及特定路径的 `Bash` 调用 — 请使用 `preToolUse` 钩子。请参阅 [扩展 Panacea](../core-concepts/extend.md)。

## 下一步

- [Panacea 的工作原理](../core-concepts/how-it-works.md) — 代理循环控制这些模式
- [探索 .anote 目录](../core-concepts/anote-directory.md) — `permissionMode` 在配置中的位置
