# 總覽

**Anote AI** 是一個統一的 AI 編程助手與私人聊天平台。它能讀取你的程式碼庫、編輯檔案、執行指令、審查 PR，並回答你文件相關的問題 — 可在終端機、IDE、瀏覽器、桌面應用程式和手機上使用。

## 開始使用

Anote 支援多種介面：CLI、VS Code、網頁、桌面與行動裝置。從下方選擇一個開始吧。大多數介面都會與代管的 Anote 後端或你自行架設的執行個體通訊（參見[設定](getting-started/configuration.md)）。

=== "CLI"

    功能完整的 CLI，可直接在終端機中使用 Anote。提問、修復錯誤、審查 PR，不需離開命令列即可搜尋你的程式碼庫。

    ```bash
    npm install -g @anote-ai/anote
    ```

    需要 Node.js 18 或更新版本。接着，在任意專案中：

    ```bash
    cd your-project
    anote init
    anote ask "explain this codebase"
    ```

    `anote init` 會引導你設定 API 金鑰與偏好的 LLM 供應商。

    [繼續前往快速入門 →](getting-started/quickstart.md)

=== "VS Code"

    VS Code 擴充功能將聊天側邊欄、內嵌差異審查與串流回應直接帶入你的編輯器。

    在 VS Code 擴充功能市集中搜尋 **「Anote」**，或透過以下方式安裝：

    ```bash
    code --install-extension anote-ai.anote-ai-coding
    ```

    [VS Code 擴充功能總覽 →](vscode/overview.md)

=== "網頁應用程式"

    ChatGPT 風格的瀏覽器聊天介面，支援文件上傳與基於 RAG 的問答。使用 Docker Compose 自行架設：

    ```bash
    git clone https://github.com/anote-ai/Panacea
    cd Panacea
    cp packages/backend/.env.example packages/backend/.env
    # 編輯 .env 填入你的 API 金鑰
    docker compose up
    ```

    前端：`http://localhost:3000` · 後端：`http://localhost:5000`

    [網頁應用程式總覽 →](web/overview.md)

=== "桌面版"

    私密且可離線使用的 Electron 應用程式。所有資料都保留在你的裝置上，當你不想使用代管供應商時，也能搭配本機 Ollama 模型運作。

    從 [GitHub Releases](https://github.com/anote-ai/Panacea/releases) 下載最新版本 — 支援 **macOS**（DMG）、**Windows**（安裝程式）與 **Linux**（AppImage/DEB/RPM）。

    [桌面應用程式總覽 →](desktop/overview.md)

=== "行動版"

    使用 Expo 建構的原生 iOS 與 Android 聊天用戶端。

    ```bash
    cd packages/mobile
    npm install
    npx expo start
    ```

    使用 Expo Go 應用程式掃描 QR code，或在模擬器中執行。

    [行動應用程式總覽 →](mobile/overview.md)

## 你可以做什麼

??? abstract "詢問關於程式碼庫的問題"

    ```bash
    anote ask "how does the authentication middleware work?"
    anote ask --file src/auth.ts "explain this file"
    anote ask --compare               # 並排比較多個模型
    cat src/handler.py | anote ask "what could go wrong here?"
    ```

??? bug "自動修復錯誤"

    `anote fix --loop` 會針對你的測試套件反覆執行 — 最多 `--max-iterations` 輪 — 直到通過為止，或使用 `--file` 修復單一檔案。

    ```bash
    anote fix --loop --max-iterations 5
    ```

??? example "審查拉取請求"

    ```bash
    anote review --pr 42
    ```

    針對錯誤、安全性問題與程式碼品質進行審查 — 可在本機對目錄/檔案進行，或直接發佈到 GitHub PR。

??? search "對程式碼庫進行語意搜尋"

    ```bash
    anote index              # 建立 TF-IDF 索引（執行一次後持續保持更新）
    anote search "JWT token validation"
    ```

??? question "針對你的文件進行聊天與問答"

    在[網頁應用程式](web/overview.md)或[桌面應用程式](desktop/overview.md)中上傳文件並提問 — 透過 `POST /api/documents/{id}/ask` 實現基於 RAG 的問答。

??? tip "稽核安全性與效能問題"

    ```bash
    anote security --severity high --fix
    anote perf --focus "database,bundle" --fix
    ```

??? note "產生變更日誌與文件，或執行遷移"

    ```bash
    anote changelog --since v1.2.0
    anote docs src/api.ts --style jsdoc
    anote migrate --from "React 17" --to "React 18"
    ```

??? info "檢查你的環境設定"

    ```bash
    anote doctor
    ```

    檢查 Node.js ≥ 18、`ANTHROPIC_API_KEY`、`.anote.json`、`CLAW.md` 與 git。

## 隨處使用 Anote

| 我想要... | 最佳選擇 |
|---|---|
| 在終端機中作業 | [CLI](cli/overview.md) |
| 在編輯器中直接獲得 AI 協助 | [VS Code 擴充功能](vscode/overview.md) |
| 在瀏覽器中與文件聊天 | [網頁應用程式](web/overview.md) |
| 保持一切私密且離線 | [桌面應用程式](desktop/overview.md) — 支援本機 Ollama 模型 |
| 從手機聊天 | [行動應用程式](mobile/overview.md) |
| 從自己的程式碼或腳本呼叫 Anote | [TypeScript SDK](sdk/typescript.md) 或 [Python SDK](sdk/python.md) |
| 直接串接 REST API | [後端 API](api/overview.md) |
| 自動化 PR 審查或 CI 檢查 | [CLI: `anote review --pr`](cli/commands.md#anote-review) |

## 支援的 LLM 供應商

- **Anthropic** — Claude（`claude-opus-4-8`、`claude-sonnet-4-6`、`claude-haiku-4-5`）
- **OpenAI** — GPT-4o、GPT-4o-mini
- **Google** — Gemini 2.0 Flash、Gemini 1.5 Pro
- **Ollama** — 任意本機模型（Llama 3、Mistral 等）
- **xAI** — Grok

## 下一步

- [快速入門](getting-started/quickstart.md) — 依序執行 init、ask、fix、index、review 與 changelog
- [Panacea 運作方式](core-concepts/how-it-works.md) — 代理迴圈、工具與串流
- [權限模式](use-panacea/permission-modes.md) — 控制代理在未經詢問下可以做什麼
- [常見工作流程](use-panacea/common-workflows.md) — 日常任務的逐步範例
- [設定](getting-started/configuration.md) — API 金鑰、供應商設定與 `~/.anote/config.json`
- [CLI 指令](cli/commands.md) — 完整的指令參考
- [後端 API](api/overview.md) — 支撐所有介面的 REST 端點
- [架構](development/architecture.md) — monorepo 與後端如何協同運作
- [貢獻指南](development/contributing.md) — 為本機開發設定儲存庫
