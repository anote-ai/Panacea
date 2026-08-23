# 概要

**Anote AI** は、統合されたAIコーディングアシスタントおよびプライベートチャットボットプラットフォームです。コードベースを読み取り、ファイルを編集し、コマンドを実行し、PRをレビューし、ドキュメントに関する質問に答えます — ターミナル、IDE、ブラウザ、デスクトップアプリ、電話で利用可能です。

## 始める

Anoteは、CLI、VS Code、ウェブ、デスクトップ、モバイルのいくつかのプラットフォームで動作します。以下から選択して始めてください。ほとんどのプラットフォームは、ホストされたAnoteバックエンドまたは自分自身でホストしたインスタンスと通信します（[設定](getting-started/configuration.md)を参照）。

=== "CLI"

    ターミナルでAnoteと直接作業するためのフル機能CLIです。質問をし、バグを修正し、PRをレビューし、シェルを離れることなくコードベースを検索します。

    ```bash
    npm install -g @anote-ai/anote
    ```

    Node.js 18以降が必要です。その後、任意のプロジェクトで：

    ```bash
    cd your-project
    anote init
    anote ask "このコードベースを説明してください"
    ```

    `anote init` は、APIキーと好みのLLMプロバイダーの設定を手助けします。

    [クイックスタートを続ける →](getting-started/quickstart.md)

=== "VS Code"

    VS Code拡張機能は、チャットサイドバー、インライン差分レビュー、ストリーミング応答をエディタに直接持ち込みます。

    VS Code拡張機能マーケットプレイスで **"Anote"** を検索するか、次のコマンドでインストールします：

    ```bash
    code --install-extension anote-ai.anote-ai-coding
    ```

    [VS Code拡張機能の概要 →](vscode/overview.md)

=== "Web App"

    ドキュメントのアップロードとRAGバックのQ&Aを備えたChatGPTスタイルのブラウザチャットインターフェースです。Docker Composeで自己ホストできます：

    ```bash
    git clone https://github.com/anote-ai/Panacea
    cd Panacea
    cp packages/backend/.env.example packages/backend/.env
    # APIキーで.envを編集
    docker compose up
    ```

    フロントエンド: `http://localhost:3000` · バックエンド: `http://localhost:5000`

    [Web Appの概要 →](web/overview.md)

=== "Desktop"

    プライベートでオフライン対応のElectronアプリです。すべてのデータはあなたのマシンに保存され、ホストされたプロバイダーに呼び出したくないときはローカルのOllamaモデルと連携します。

    [GitHub Releases](https://github.com/anote-ai/Panacea/releases) から最新のリリースをダウンロード — **macOS** (DMG)、**Windows** (インストーラー)、および **Linux** (AppImage/DEB/RPM) 用に利用可能です。

    [デスクトップアプリの概要 →](desktop/overview.md)

=== "Mobile"

    Expoで構築されたネイティブiOSおよびAndroidチャットクライアントです。

    ```bash
    cd packages/mobile
    npm install
    npx expo start
    ```

    Expo GoアプリでQRコードをスキャンするか、シミュレーターで実行します。

    [モバイルアプリの概要 →](mobile/overview.md)

## できること

??? abstract "コードベースに関する質問をする"

    ```bash
    anote ask "認証ミドルウェアはどのように機能しますか？"
    anote ask --file src/auth.ts "このファイルを説明してください"
    anote ask --compare               # 複数のモデル間で並べて比較
    cat src/handler.py | anote ask "ここで何が問題になる可能性がありますか？"
    ```

??? bug "バグを自動的に修正する"

    `anote fix --loop` は、テストスイートに対して繰り返し実行します — `--max-iterations` ラウンドまで — それが通過するか、`--file` で単一のファイルを修正するまで。

    ```bash
    anote fix --loop --max-iterations 5
    ```

??? example "プルリクエストをレビューする"

    ```bash
    anote review --pr 42
    ```

    バグ、セキュリティ問題、品質のレビュー — ディレクトリ/ファイルに対してローカルで、またはGitHub PRに直接投稿します。

??? search "コードベースを意味的に検索する"

    ```bash
    anote index              # TF-IDFインデックスを構築（1回実行し、その後更新を維持）
    anote search "JWTトークンの検証"
    ```

??? question "ドキュメントに関するチャットとQ&A"

    [Web App](web/overview.md) または [Desktop App](desktop/overview.md) にドキュメントをアップロードし、それに対して質問します — `POST /api/documents/{id}/ask` を介してRAGバック。

??? tip "セキュリティとパフォーマンスの問題を監査する"

    ```bash
    anote security --severity high --fix
    anote perf --focus "database,bundle" --fix
    ```

??? note "変更履歴やドキュメントを生成する、またはマイグレーションを実行する"

    ```bash
    anote changelog --since v1.2.0
    anote docs src/api.ts --style jsdoc
    anote migrate --from "React 17" --to "React 18"
    ```

??? info "セットアップを確認する"

    ```bash
    anote doctor
    ```

    Node.js ≥ 18、`ANTHROPIC_API_KEY`、`.anote.json`、`CLAW.md`、およびgitをチェックします。

## Anoteをどこでも使用する

| やりたいこと | 最適なオプション |
|---|---|
| ターミナルから作業する | [CLI](cli/overview.md) |
| エディタでインラインAIヘルプを得る | [VS Code拡張機能](vscode/overview.md) |
| ブラウザでドキュメントとチャットする | [Web App](web/overview.md) |
| すべてをプライベートかつオフラインに保つ | [デスクトップアプリ](desktop/overview.md) — ローカルのOllamaモデルと連携 |
| 電話からチャットする | [モバイルアプリ](mobile/overview.md) |
| 自分のコードやスクリプトからAnoteを呼び出す | [TypeScript SDK](sdk/typescript.md) または [Python SDK](sdk/python.md) |
| REST APIに直接統合する | [バックエンドAPI](api/overview.md) |
| PRレビューやCIチェックを自動化する | [CLI: `anote review --pr`](cli/commands.md#anote-review) |

## サポートされているLLMプロバイダー

- **Anthropic** — Claude (`claude-opus-4-8`, `claude-sonnet-4-6`, `claude-haiku-4-5`)
- **OpenAI** — GPT-4o, GPT-4o-mini
- **Google** — Gemini 2.0 Flash, Gemini 1.5 Pro
- **Ollama** — 任意のローカルモデル (Llama 3, Mistral など)
- **xAI** — Grok

## 次のステップ

- [クイックスタート](getting-started/quickstart.md) — 初期化、質問、修正、インデックス、レビュー、変更履歴を順に
- [Panaceaの仕組み](core-concepts/how-it-works.md) — エージェントループ、ツール、ストリーミング
- [権限モード](use-panacea/permission-modes.md) — エージェントが何をできるかを尋ねずに制御
- [一般的なワークフロー](use-panacea/common-workflows.md) — 日常的なタスクのためのステップバイステップパターン
- [設定](getting-started/configuration.md) — APIキー、プロバイダー設定、および `~/.anote/config.json`
- [CLIコマンド](cli/commands.md) — 完全なコマンドリファレンス
- [バックエンドAPI](api/overview.md) — すべてのプラットフォームを支えるRESTエンドポイント
- [アーキテクチャ](development/architecture.md) — モノレポとバックエンドの統合
- [貢献](development/contributing.md) — ローカル開発のためのリポジトリのセットアップ
