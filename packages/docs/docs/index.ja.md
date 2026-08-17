# 概要

**Anote AI** は、統合されたAIコーディングアシスタント兼プライベートチャットプラットフォームです。コードベースを読み取り、ファイルを編集し、コマンドを実行し、プルリクエストをレビューし、ドキュメントに関する質問に回答します — ターミナル、IDE、ブラウザ、デスクトップアプリ、スマートフォンで利用できます。

## はじめに

Anote は複数のサーフェスで動作します：CLI、VS Code、Web、デスクトップ、モバイル。下から1つ選んで始めましょう。ほとんどのサーフェスは、ホストされたAnoteバックエンドまたは自分でホストするインスタンスと通信します（[設定](getting-started/configuration.md)を参照）。

=== "CLI"

    ターミナルで直接Anoteを利用できる、フル機能のCLIです。質問したり、バグを修正したり、プルリクエストをレビューしたり、シェルを離れずにコードベースを検索したりできます。

    ```bash
    npm install -g @anote-ai/anote
    ```

    Node.js 18以降が必要です。その後、任意のプロジェクトで：

    ```bash
    cd your-project
    anote init
    anote ask "explain this codebase"
    ```

    `anote init` はAPIキーと優先するLLMプロバイダーの設定をガイドします。

    [クイックスタートに進む →](getting-started/quickstart.md)

=== "VS Code"

    VS Code拡張機能は、チャットサイドバー、インラインdiffレビュー、ストリーミング応答をエディタに直接統合します。

    VS Code拡張機能マーケットプレイスで **「Anote」** を検索するか、以下でインストールしてください：

    ```bash
    code --install-extension anote-ai.anote-ai-coding
    ```

    [VS Code拡張機能の概要 →](vscode/overview.md)

=== "Webアプリ"

    ChatGPTスタイルのブラウザチャットインターフェースで、ドキュメントのアップロードとRAGベースのQ&Aに対応しています。Docker Composeでセルフホストできます：

    ```bash
    git clone https://github.com/anote-ai/Panacea
    cd Panacea
    cp packages/backend/.env.example packages/backend/.env
    # .env をAPIキーで編集
    docker compose up
    ```

    フロントエンド：`http://localhost:3000` · バックエンド：`http://localhost:5000`

    [Webアプリの概要 →](web/overview.md)

=== "デスクトップ"

    プライベートでオフライン対応のElectronアプリです。すべてのデータはお使いのマシン上に残り、ホストされたプロバイダーを使いたくない場合はローカルのOllamaモデルでも動作します。

    [GitHub Releases](https://github.com/anote-ai/Panacea/releases) から最新版をダウンロードしてください — **macOS**（DMG）、**Windows**（インストーラー）、**Linux**（AppImage/DEB/RPM）に対応しています。

    [デスクトップアプリの概要 →](desktop/overview.md)

=== "モバイル"

    Expoで構築されたネイティブのiOS・Androidチャットクライアントです。

    ```bash
    cd packages/mobile
    npm install
    npx expo start
    ```

    Expo Goアプリで QRコードをスキャンするか、シミュレーターで実行してください。

    [モバイルアプリの概要 →](mobile/overview.md)

## できること

??? abstract "コードベースについて質問する"

    ```bash
    anote ask "how does the authentication middleware work?"
    anote ask --file src/auth.ts "explain this file"
    anote ask --compare               # 複数モデルを並べて比較
    cat src/handler.py | anote ask "what could go wrong here?"
    ```

??? bug "バグを自動的に修正する"

    `anote fix --loop` はテストスイートに対して繰り返し実行され — 最大 `--max-iterations` 回まで — 成功するまで、または `--file` で単一ファイルを修正します。

    ```bash
    anote fix --loop --max-iterations 5
    ```

??? example "プルリクエストをレビューする"

    ```bash
    anote review --pr 42
    ```

    バグ、セキュリティ問題、品質のレビュー — ディレクトリ/ファイルに対してローカルで、またはGitHub PRに直接投稿します。

??? search "コードベースをセマンティック検索する"

    ```bash
    anote index              # TF-IDFインデックスを構築（一度実行後、最新に保つ）
    anote search "JWT token validation"
    ```

??? question "ドキュメントについてチャット・質問する"

    [Webアプリ](web/overview.md) または [デスクトップアプリ](desktop/overview.md) でドキュメントをアップロードして質問できます — `POST /api/documents/{id}/ask` によるRAGベースです。

??? tip "セキュリティとパフォーマンスを監査する"

    ```bash
    anote security --severity high --fix
    anote perf --focus "database,bundle" --fix
    ```

??? note "変更履歴やドキュメントを生成、またはマイグレーションを実行する"

    ```bash
    anote changelog --since v1.2.0
    anote docs src/api.ts --style jsdoc
    anote migrate --from "React 17" --to "React 18"
    ```

??? info "セットアップを確認する"

    ```bash
    anote doctor
    ```

    Node.js ≥ 18、`ANTHROPIC_API_KEY`、`.anote.json`、`CLAW.md`、gitを確認します。

## どこでもAnoteを使う

| したいこと | 最適な選択肢 |
|---|---|
| ターミナルから作業する | [CLI](cli/overview.md) |
| エディタ内でAIの支援を受ける | [VS Code拡張機能](vscode/overview.md) |
| ブラウザでドキュメントについてチャットする | [Webアプリ](web/overview.md) |
| すべてをプライベートかつオフラインに保つ | [デスクトップアプリ](desktop/overview.md) — ローカルOllamaモデルで動作 |
| スマートフォンからチャットする | [モバイルアプリ](mobile/overview.md) |
| 自分のコードやスクリプトからAnoteを呼び出す | [TypeScript SDK](sdk/typescript.md) または [Python SDK](sdk/python.md) |
| REST APIに直接統合する | [バックエンドAPI](api/overview.md) |
| PRレビューやCIチェックを自動化する | [CLI: `anote review --pr`](cli/commands.md#anote-review) |

## サポートされているLLMプロバイダー

- **Anthropic** — Claude（`claude-opus-4-8`、`claude-sonnet-4-6`、`claude-haiku-4-5`）
- **OpenAI** — GPT-4o、GPT-4o-mini
- **Google** — Gemini 2.0 Flash、Gemini 1.5 Pro
- **Ollama** — 任意のローカルモデル（Llama 3、Mistralなど）
- **xAI** — Grok

## 次のステップ

- [クイックスタート](getting-started/quickstart.md) — init、ask、fix、index、review、changelogの順に
- [Panaceaの仕組み](core-concepts/how-it-works.md) — エージェントループ、ツール、ストリーミング
- [権限モード](use-panacea/permission-modes.md) — エージェントが確認なしで実行できる範囲を制御
- [一般的なワークフロー](use-panacea/common-workflows.md) — 日常タスクのステップバイステップパターン
- [設定](getting-started/configuration.md) — APIキー、プロバイダー設定、`~/.anote/config.json`
- [CLIコマンド](cli/commands.md) — 完全なコマンドリファレンス
- [バックエンドAPI](api/overview.md) — すべてのサーフェスを支えるRESTエンドポイント
- [アーキテクチャ](development/architecture.md) — モノレポとバックエンドの構成
- [コントリビュート](development/contributing.md) — ローカル開発用にリポジトリをセットアップ
