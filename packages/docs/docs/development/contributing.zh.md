# 贡献

## 设置

```bash
git clone https://github.com/anote-ai/Panacea
cd Panacea

# 安装 Node.js 包
npm install

# 设置 Python 后端
cd packages/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# 使用你的密钥编辑 .env

# 启动所有服务
cd ../.. 
docker compose up
```

## 开发工作流程

1. 从 `main` 创建一个功能分支
2. 在相关的 `packages/` 目录中进行更改
3. 运行测试：`make test`
4. 运行代码检查工具：`make lint`
5. 提交拉取请求

## 测试

```bash
# 所有测试
make test

# 仅后端
make test-backend

# 仅 TypeScript
make test-ts
```

## 代码标准

### Python (后端)
- **Ruff** 用于代码检查 (`ruff check .`)
- **Mypy** 用于类型检查 (`mypy .`)
- **Pytest** 用于测试 (≥80% 覆盖率)
- 对所有新函数进行类型注解

### TypeScript (前端/cli/sdk)
- **ESLint** 用于代码检查
- **Vitest** 或 **Jest** 用于测试
- 严格的 TypeScript (`"strict": true`)

## CI

GitHub Actions 在每次推送时运行：
1. 后端：ruff → mypy → pytest (80% 覆盖率门槛)
2. TypeScript：构建 → 测试
3. VS Code：构建扩展
4. 文档：构建 MkDocs 网站
