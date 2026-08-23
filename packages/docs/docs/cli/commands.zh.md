# CLI 命令

## `anote ask`

询问关于您代码的任何问题。

```bash
anote ask "身份验证中间件是如何工作的？"
anote ask --file src/auth.ts "解释这个文件"
anote ask --compare  # 在多个模型之间并排比较
cat file.py | anote ask "查找错误"
```

## `anote fix`

修复当前目录中的错误。

```bash
anote fix
anote fix --loop                    # 迭代直到测试通过
anote fix --max-iterations 5        # 限制迭代次数
anote fix --file src/broken.ts      # 修复特定文件
```

## `anote review`

审查代码中的错误、安全问题和质量。

```bash
anote review                        # 审查当前目录
anote review --file src/handler.ts  # 审查特定文件
anote review --pr 42                # 在 GitHub PR 上发布 AI 审查
```

## `anote index`

构建您的代码库的 TF-IDF 语义搜索索引。

```bash
anote index              # 索引当前目录
anote index --watch      # 监视更改并重新索引
anote index /path/to/dir # 索引特定目录
```

## `anote search`

语义搜索您的索引代码库。

```bash
anote search "JWT 令牌验证"
anote search "数据库连接" --top 10
anote search "身份验证中间件" --json
```

## `anote doctor`

检查您的环境以发现配置问题。

```bash
anote doctor
```

检查项：Node.js ≥ 18，设置 `ANTHROPIC_API_KEY`，存在 `.anote.json`，存在 `CLAW.md`，已安装 git。

## `anote changelog`

从 git 历史生成 CHANGELOG.md 条目。

```bash
anote changelog
anote changelog --since v1.2.0
anote changelog --dry-run
```

## `anote docs`

为未记录的代码生成文档。

```bash
anote docs
anote docs src/api.ts
anote docs --style jsdoc
anote docs --dry-run
```

## `anote migrate`

AI 辅助的代码库迁移。

```bash
anote migrate --from "React 17" --to "React 18"
anote migrate --from "axios" --to "fetch"
anote migrate --dry-run
```

## `anote security`

对您的代码库进行安全审计（OWASP 前 10）。

```bash
anote security
anote security --severity high
anote security --fix
```

## `anote perf`

性能分析。

```bash
anote perf
anote perf --focus "数据库,包"
anote perf --fix
```
