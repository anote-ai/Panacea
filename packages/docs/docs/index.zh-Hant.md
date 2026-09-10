# 概述

**Ourogen** 是一個統一的 AI 編碼助手和私人聊天機器人平台。它可以讀取您的程式碼庫、編輯檔案、執行命令、審查 PR，並回答有關您的文件的問題 — 可在您的終端、IDE、瀏覽器、桌面應用程式和手機上使用。

## 開始使用

Anote 可以在幾個平台上運行：CLI、VS Code、網頁、桌面和移動設備。請選擇下面的一個開始使用。大多數平台都與託管的 Anote 後端或您自己的自託管實例進行通信（請參見 [配置](getting-started/configuration.md)）。

=== "CLI"

    在終端中直接使用 Anote 的全功能 CLI。提出問題、修復錯誤、審查 PR，並在不離開 shell 的情況下搜索您的程式碼庫。

    ```bash
    npm install -g @anote-ai/anote
    ```

    需要 Node.js 18 或更高版本。然後，在任何專案中：

    ```bash
    cd your-project
    anote init
    anote ask "explain this codebase"
    ```

    `anote init` 將引導您設置 API 金鑰和首選 LLM 提供者。

    [繼續快速入門 →](getting-started/quickstart.md)

=== "VS Code"

    VS Code 擴展帶來了聊天側邊欄、內聯差異審查和直接在編輯器中流式響應。

    在 VS Code 擴展市場中搜索 **"Anote"**，或通過以下方式安裝：

    ```bash
    code --install-extension anote-ai.anote-ai-coding
    ```

    [VS Code 擴展概述 →](vscode/overview.md)

=== "網頁應用程式"

    一個 ChatGPT 風格的瀏覽器聊天介面，具有文件上傳和 RAG 支持的問答功能。使用 Docker Compose 自行託管：

    ```bash
    git clone https://github.com/anote-ai/Panacea
    cd Panacea
    cp packages/backend/.env.example packages/backend/.env
    # 使用您的 API 金鑰編輯 .env
    docker compose up
    ```

    前端：`http://localhost:3000` · 後端：`http://localhost:5000`

    [網頁應用程式概述 →](web/overview.md)

=== "桌面"

    一個私有的、具備離線功能的 Electron 應用程式。所有數據都保留在您的機器上，並且當您不想呼叫託管提供者時，它可以與本地 Ollama 模型一起使用。

    從 [GitHub Releases](https://github.com/anote-ai/Panacea/releases) 下載最新版本 — 可用於 **macOS** (DMG)、**Windows** (安裝程式) 和 **Linux** (AppImage/DEB/RPM)。

    [桌面應用程式概述 →](desktop/overview.md)

=== "移動"

    一個使用 Expo 構建的原生 iOS 和 Android 聊天客戶端。

    ```bash
    cd packages/mobile
    npm install
    npx expo start
    ```

    使用 Expo Go 應用程式掃描 QR 碼，或在模擬器中運行。

    [移動應用程式概述 →](mobile/overview.md)

## 您可以做什麼

??? abstract "詢問有關您的程式碼庫的問題"

    ```bash
    anote ask "how does the authentication middleware work?"
    anote ask --file src/auth.ts "explain this file"
    anote ask --compare               # 在多個模型之間進行並排比較
    cat src/handler.py | anote ask "what could go wrong here?"
    ```

??? bug "自動修復錯誤"

    `anote fix --loop` 對您的測試套件進行迭代 — 直到通過為止，最多 `--max-iterations` 輪次 — 或使用 `--file` 修復單個檔案。

    ```bash
    anote fix --loop --max-iterations 5
    ```

??? example "審查拉取請求"

    ```bash
    anote review --pr 42
    ```

    審查錯誤、安全問題和質量 — 在本地對目錄/檔案進行審查，或直接發佈到 GitHub PR。

??? search "語義搜索您的程式碼庫"

    ```bash
    anote index              # 建立 TF-IDF 索引（運行一次，然後保持更新）
    anote search "JWT token validation"
    ```

??? question "對您的文件進行聊天和問答"

    在 [網頁應用程式](web/overview.md) 或 [桌面應用程式](desktop/overview.md) 中上傳文件並對其提出問題 — 通過 `POST /api/documents/{id}/ask` 進行 RAG 支持。

??? tip "審核安全性和性能問題"

    ```bash
    anote security --severity high --fix
    anote perf --focus "database,bundle" --fix
    ```

??? note "生成變更日誌和文檔，或運行遷移"

    ```bash
    anote changelog --since v1.2.0
    anote docs src/api.ts --style jsdoc
    anote migrate --from "React 17" --to "React 18"
    ```

??? info "檢查您的設置"

    ```bash
    anote doctor
    ```

    檢查 Node.js ≥ 18、`ANTHROPIC_API_KEY`、`.anote.json`、`CLAW.md` 和 git。

## 在各處使用 Anote

| 我想要... | 最佳選擇 |
|---|---|
| 從我的終端工作 | [CLI](cli/overview.md) |
| 在我的編輯器中獲得內聯 AI 幫助 | [VS Code 擴展](vscode/overview.md) |
| 在瀏覽器中與文件聊天 | [網頁應用程式](web/overview.md) |
| 保持所有內容私密且離線 | [桌面應用程式](desktop/overview.md) — 與本地 Ollama 模型一起使用 |
| 從我的手機聊天 | [移動應用程式](mobile/overview.md) |
| 從我自己的程式碼或腳本呼叫 Anote | [TypeScript SDK](sdk/typescript.md) 或 [Python SDK](sdk/python.md) |
| 直接與 REST API 集成 | [後端 API](api/overview.md) |
| 自動化 PR 審查或 CI 檢查 | [CLI: `anote review --pr`](cli/commands.md#anote-review) |

## 支援的 LLM 提供者

- **Anthropic** — Claude (`claude-opus-4-8`, `claude-sonnet-4-6`, `claude-haiku-4-5`)
- **OpenAI** — GPT-4o, GPT-4o-mini
- **Google** — Gemini 2.0 Flash, Gemini 1.5 Pro
- **Ollama** — 任何本地模型 (Llama 3, Mistral, 等)
- **xAI** — Grok

## 下一步

- [快速入門](getting-started/quickstart.md) — 按順序初始化、詢問、修復、索引、審查和變更日誌
- [Panacea 的運作方式](core-concepts/how-it-works.md) — 代理循環、工具和流式傳輸
- [權限模式](use-panacea/permission-modes.md) — 控制代理可以在不詢問的情況下執行的操作
- [常見工作流程](use-panacea/common-workflows.md) — 日常任務的逐步模式
- [配置](getting-started/configuration.md) — API 金鑰、提供者設置和 `~/.anote/config.json`
- [CLI 命令](cli/commands.md) — 完整的命令參考
- [後端 API](api/overview.md) — 為每個平台提供支持的 REST 端點
- [架構](development/architecture.md) — 單一代碼庫和後端如何協同工作
- [貢獻](development/contributing.md) — 設置本地開發的代碼庫
