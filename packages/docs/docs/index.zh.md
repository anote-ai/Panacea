# 概览

**Anote AI** 是一个统一的 AI 编程助手和私有聊天平台。它可以读取你的代码库、编辑文件、运行命令、审查 PR，并回答有关你文档的问题 — 可在终端、IDE、浏览器、桌面应用和手机上使用。

## 开始使用

Anote 支持多种使用界面：CLI、VS Code、网页、桌面和移动端。从下面选择一个开始吧。大多数界面都会与托管的 Anote 后端或你自己的自托管实例通信（参见[配置](getting-started/configuration.md)）。

=== "CLI"

    功能齐全的 CLI，可直接在终端中使用 Anote。提问、修复 bug、审查 PR，无需离开命令行即可搜索你的代码库。

    ```bash
    npm install -g @anote-ai/anote
    ```

    需要 Node.js 18 或更高版本。然后，在任意项目中：

    ```bash
    cd your-project
    anote init
    anote ask "explain this codebase"
    ```

    `anote init` 会引导你设置 API 密钥和首选的 LLM 提供商。

    [继续查看快速入门 →](getting-started/quickstart.md)

=== "VS Code"

    VS Code 扩展将聊天侧边栏、内联 diff 审查和流式响应直接带入你的编辑器。

    在 VS Code 扩展市场中搜索 **"Anote"**，或通过以下方式安装：

    ```bash
    code --install-extension anote-ai.anote-ai-coding
    ```

    [VS Code 扩展概览 →](vscode/overview.md)

=== "网页应用"

    ChatGPT 风格的浏览器聊天界面，支持文档上传和基于 RAG 的问答。使用 Docker Compose 自托管：

    ```bash
    git clone https://github.com/anote-ai/Panacea
    cd Panacea
    cp packages/backend/.env.example packages/backend/.env
    # 编辑 .env 填入你的 API 密钥
    docker compose up
    ```

    前端：`http://localhost:3000` · 后端：`http://localhost:5000`

    [网页应用概览 →](web/overview.md)

=== "桌面端"

    私密、可离线使用的 Electron 应用。所有数据都保留在你的设备上，当你不想使用托管提供商时，它也能配合本地 Ollama 模型工作。

    从 [GitHub Releases](https://github.com/anote-ai/Panacea/releases) 下载最新版本 — 支持 **macOS**（DMG）、**Windows**（安装程序）和 **Linux**（AppImage/DEB/RPM）。

    [桌面应用概览 →](desktop/overview.md)

=== "移动端"

    使用 Expo 构建的原生 iOS 和 Android 聊天客户端。

    ```bash
    cd packages/mobile
    npm install
    npx expo start
    ```

    使用 Expo Go 应用扫描二维码，或在模拟器中运行。

    [移动应用概览 →](mobile/overview.md)

## 你可以做什么

??? abstract "询问关于代码库的问题"

    ```bash
    anote ask "how does the authentication middleware work?"
    anote ask --file src/auth.ts "explain this file"
    anote ask --compare               # 并排比较多个模型
    cat src/handler.py | anote ask "what could go wrong here?"
    ```

??? bug "自动修复 bug"

    `anote fix --loop` 会针对你的测试套件反复迭代 — 最多 `--max-iterations` 轮 — 直到通过为止，或使用 `--file` 修复单个文件。

    ```bash
    anote fix --loop --max-iterations 5
    ```

??? example "审查拉取请求"

    ```bash
    anote review --pr 42
    ```

    针对 bug、安全问题和代码质量进行审查 — 可以在本地对目录/文件进行，也可以直接发布到 GitHub PR。

??? search "对代码库进行语义搜索"

    ```bash
    anote index              # 构建 TF-IDF 索引（运行一次，之后保持更新）
    anote search "JWT token validation"
    ```

??? question "就你的文档进行聊天和问答"

    在[网页应用](web/overview.md)或[桌面应用](desktop/overview.md)中上传文档并提问 — 通过 `POST /api/documents/{id}/ask` 实现基于 RAG 的问答。

??? tip "审计安全性和性能问题"

    ```bash
    anote security --severity high --fix
    anote perf --focus "database,bundle" --fix
    ```

??? note "生成变更日志和文档，或执行迁移"

    ```bash
    anote changelog --since v1.2.0
    anote docs src/api.ts --style jsdoc
    anote migrate --from "React 17" --to "React 18"
    ```

??? info "检查你的环境配置"

    ```bash
    anote doctor
    ```

    检查 Node.js ≥ 18、`ANTHROPIC_API_KEY`、`.anote.json`、`CLAW.md` 和 git。

## 随处使用 Anote

| 我想... | 最佳选择 |
|---|---|
| 在终端中工作 | [CLI](cli/overview.md) |
| 在编辑器中直接获得 AI 帮助 | [VS Code 扩展](vscode/overview.md) |
| 在浏览器中与文档聊天 | [网页应用](web/overview.md) |
| 保持一切私密且离线 | [桌面应用](desktop/overview.md) — 支持本地 Ollama 模型 |
| 从手机聊天 | [移动应用](mobile/overview.md) |
| 从自己的代码或脚本调用 Anote | [TypeScript SDK](sdk/typescript.md) 或 [Python SDK](sdk/python.md) |
| 直接对接 REST API | [后端 API](api/overview.md) |
| 自动化 PR 审查或 CI 检查 | [CLI: `anote review --pr`](cli/commands.md#anote-review) |

## 支持的 LLM 提供商

- **Anthropic** — Claude（`claude-opus-4-8`、`claude-sonnet-4-6`、`claude-haiku-4-5`）
- **OpenAI** — GPT-4o、GPT-4o-mini
- **Google** — Gemini 2.0 Flash、Gemini 1.5 Pro
- **Ollama** — 任意本地模型（Llama 3、Mistral 等）
- **xAI** — Grok

## 下一步

- [快速入门](getting-started/quickstart.md) — 按顺序执行 init、ask、fix、index、review 和 changelog
- [Panacea 工作原理](core-concepts/how-it-works.md) — 智能体循环、工具与流式传输
- [权限模式](use-panacea/permission-modes.md) — 控制智能体在不询问的情况下可以做什么
- [常见工作流](use-panacea/common-workflows.md) — 日常任务的分步模式
- [配置](getting-started/configuration.md) — API 密钥、提供商设置和 `~/.anote/config.json`
- [CLI 命令](cli/commands.md) — 完整的命令参考
- [后端 API](api/overview.md) — 支撑所有界面的 REST 端点
- [架构](development/architecture.md) — monorepo 与后端如何协同工作
- [贡献指南](development/contributing.md) — 为本地开发配置代码仓库
