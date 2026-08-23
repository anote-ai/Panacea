# 快速开始

## 1. 初始化

```bash
anote init
```

这将引导您设置您的 API 密钥和首选的 LLM 提供商。

## 2. 提问

```bash
# 一般问题
anote ask "这个代码库中的身份验证是如何工作的？"

# 关注文件
anote ask --file src/auth.ts "解释一下这个"

# 管道代码
cat src/handler.py | anote ask "这里可能出什么问题？"
```

## 3. 自动修复错误

```bash
# 修复并迭代直到测试通过（最多 5 轮）
anote fix --loop --max-iterations 5
```

## 4. 进行语义搜索索引

```bash
# 索引您的代码库（运行一次，然后保持更新）
anote index

# 进行语义搜索
anote search "JWT 令牌验证"
anote search "数据库连接池"
```

## 5. 审查 PR

```bash
anote review --pr 42
```

## 6. 生成变更日志

```bash
anote changelog --since v1.2.0
```
