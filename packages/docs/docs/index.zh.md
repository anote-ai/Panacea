# 概述

**Anote AI** 是一个统一的 AI 编码助手和私人聊天机器人平台。它可以读取您的代码库、编辑文件、运行命令、审查 PR，并回答您文档中的问题——可在您的终端、IDE、浏览器、桌面应用程序和手机上使用。

## 开始使用

Anote 可以在多个平台上运行：CLI、VS Code、网页、桌面和移动设备。选择下面的一个开始使用。大多数平台与托管的 Anote 后端或您自己的自托管实例进行通信（请参见 [配置](getting-started/configuration.md)）。

=== "CLI"

    在终端中直接与 Anote 交互的功能齐全的 CLI。提出问题、修复错误、审查 PR，并在不离开 shell 的情况下搜索您的代码库。

    ```bash
    npm install -g @anote-ai/anote
    ```

    需要 Node.js 18 或更高版本。然后，在任何项目中：

    ```bash
    cd your-project
    anote init
    anote ask "explain this codebase"
    ```

    `anote init` 将引导您设置 API 密钥和首选 LLM 提供商。

    [继续快速入门 →](getting-started/quickstart.md)

=== "VS Code"

    VS Code 扩展带来了聊天侧边栏、内联差异审查和直接在编辑器中流式响应。

    在 VS Code 扩展市场中搜索 **"Anote"**，或通过以下方式安装：

    ```bash
    code --install-extension anote-ai.anote-ai-coding
    ```

    [VS Code 扩展概述 →](vscode/overview.md)

=== "Web App"

    类似 ChatGPT 的浏览器聊天界面，支持文档上传和基于 RAG 的问答。使用 Docker Compose 自托管：

    ```bash
    git clone https://github.com/anote-ai/Panacea
    cd Panacea
    cp packages/backend/.env.example packages/backend/.env
    # 使用您的 API 密钥编辑 .env
    docker compose up
    ```

    前端：`http://localhost:3000` · 后端：`http://localhost:5000`

    [Web App 概述 →](web/overview.md)

=== "Desktop"

    一个私人、离线可用的 Electron 应用程序。所有数据保留在您的机器上，当您不想调用托管提供商时，它可以与本地 Ollama 模型一起使用。

    从 [GitHub Releases](https://github.com/anote-ai/Panacea/releases) 下载最新版本——适用于 **macOS**（DMG）、**Windows**（安装程序）和 **Linux**（AppImage/DEB/RPM）。

    [桌面应用程序概述 →](desktop/overview.md)

=== "Mobile"

    一个使用 Expo 构建的原生 iOS 和 Android 聊天客户端。

    ```bash
    cd packages/mobile
    npm install
    npx expo start
    ```

    使用 Expo Go 应用扫描二维码，或在模拟器中运行。

    [移动应用程序概述 →](mobile/overview.md)

## 您可以做什么

??? abstract "询问有关您的代码库的问题"

    ```bash
    anote ask "how does the authentication middleware work?"
    anote ask --file src/auth.ts "explain this file"
    anote ask --compare               # 在多个模型之间并排比较
    cat src/handler.py | anote ask "what could go wrong here?"
    ```

??? bug "自动修复错误"

    `anote fix --loop` 在您的测试套件中迭代——最多 `--max-iterations` 轮——直到通过，或使用 `--file` 修复单个文件。

    ```bash
    anote fix --loop --max-iterations 5
    ```

??? example "审查拉取请求"

    ```bash
    anote review --pr 42
    ```

    针对错误、安全问题和质量进行审查——在目录/文件本地审查，或直接发布到 GitHub PR。

??? search "语义搜索您的代码库"

    ```bash
    anote index              # 构建 TF-IDF 索引（运行一次，然后保持更新）
    anote search "JWT token validation"
    ```

??? question "在您的文档上进行聊天和问答"

    在 [Web App](web/overview.md) 或 [Desktop App](desktop/overview.md) 中上传文档并针对它们提问——通过 `POST /api/documents/{id}/ask` 进行 RAG 支持。

??? tip "审计安全和性能问题"

    ```bash
    anote security --severity high --fix
    anote perf --focus "database,bundle" --fix
    ```

??? note "生成变更日志和文档，或运行迁移"

    ```bash
    anote changelog --since v1.2.0
    anote docs src/api.ts --style jsdoc
    anote migrate --from "React 17" --to "React 18"
    ```

??? info "检查您的设置"

    ```bash
    anote doctor
    ```

    检查 Node.js ≥ 18、`ANTHROPIC_API_KEY`、`.anote.json`、`CLAW.md` 和 git。

## 在任何地方使用 Anote

| 我想要... | 最佳选项 |
|---|---|
| 从我的终端工作 | [CLI](cli/overview.md) |
| 在我的编辑器中获得内联 AI 帮助 | [VS Code 扩展](vscode/overview.md) |
| 在浏览器中与文档聊天 | [Web App](web/overview.md) |
| 保持一切私密和离线 | [桌面应用程序](desktop/overview.md) — 与本地 Ollama 模型一起使用 |
| 从我的手机聊天 | [移动应用程序](mobile/overview.md) |
| 从我自己的代码或脚本调用 Anote | [TypeScript SDK](sdk/typescript.md) 或 [Python SDK](sdk/python.md) |
| 直接集成 REST API | [后端 API](api/overview.md) |
| 自动化 PR 审查或 CI 检查 | [CLI: `anote review --pr`](cli/commands.md#anote-review) |

## 支持的 LLM 提供商

- **Anthropic** — Claude (`claude-opus-4-8`, `claude-sonnet-4-6`, `claude-haiku-4-5`)
- **OpenAI** — GPT-4o, GPT-4o-mini
- **Google** — Gemini 2.0 Flash, Gemini 1.5 Pro
- **Ollama** — 任何本地模型（Llama 3、Mistral 等）
- **xAI** — Grok

## 下一步

- [快速入门](getting-started/quickstart.md) — 按顺序初始化、提问、修复、索引、审查和生成变更日志
- [Panacea 的工作原理](core-concepts/how-it-works.md) — 代理循环、工具和流式处理
- [权限模式](use-panacea/permission-modes.md) — 控制代理可以做什么而无需询问
- [常见工作流程](use-panacea/common-workflows.md) — 日常任务的逐步模式
- [配置](getting-started/configuration.md) — API 密钥、提供商设置和 `~/.anote/config.json`
- [CLI 命令](cli/commands.md) — 完整的命令参考
- [后端 API](api/overview.md) — 支持每个平台的 REST 端点
- [架构](development/architecture.md) — 单一代码库和后端如何结合
- [贡献](development/contributing.md) — 设置本地开发的代码库
