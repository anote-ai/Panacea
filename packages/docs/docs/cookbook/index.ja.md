# クックブックの概要

Panaceaクックブックは、Panaceaのプラットフォーム機能がどのように動作するかを示す実装ガイドのセットです — ドキュメントの取り込みとRAG、マルチエージェントオーケストレーション、請求、MCPツールサーバーなど。各ガイドは、関与する実際のバックエンドファイルを指し示し、そのシステムの一部をローカルで実行する方法を説明します。

ソース: [anote-ai/Cookbook](https://github.com/anote-ai/Cookbook)。

## レシピ

| レシピ | 説明 |
|---|---|
| [ドキュメントQ&A + RAG](03-panacea-document-qa-rag.md) | Panaceaのプライベートドキュメント取り込み、取得、および基盤となる回答ワークフローを理解する |
| [マルチエージェントオーケストレーション](04-panacea-multi-agent-orchestration.md) | Panaceaがタスクをオーケストレーター、エージェント、クルー、およびワークフローを通じてどのようにルーティングするかを学ぶ |
| [AIコーディングツールチェーン](05-panacea-ai-coding-toolchain.md) | CLI、VS Code、およびそのSDKを通じてPanaceaがどのようにコーディング支援を提供するかを探る |
| [マルチモーダルドキュメント取り込み](06-panacea-multimodal-ingestion.md) | Panaceaがどのように画像、音声、動画、およびスプレッドシートを同じRAGパイプラインを通じて検索可能にするかを理解する |
| [OpenAI互換APIゲートウェイ](07-panacea-openai-compatible-gateway.md) | コードの変更なしで任意のOpenAI-SDKベースのツールをPanaceaに向ける |
| [請求、APIキー & クレジットメーター](08-panacea-billing-and-api-keys.md) | Stripeのサブスクリプション、APIキー、およびリクエストごとのクレジットメーターがどのように組み合わさるかを学ぶ |
| [MCPツールサーバー](09-panacea-mcp-tool-server.md) | Panaceaのドキュメント/チャットのプリミティブをClaude Desktopおよび他のMCPクライアント用の標準MCPツールとして公開する |
| [マルチチャネルメッセージングボット](10-panacea-messaging-bots.md) | Slack、SMS、およびWhatsAppからPanaceaにコーディング質問をする |

## レシピをローカルで実行する

ほとんどのレシピは、完全なPanaceaスタックに対して実行されます：

```bash
cp packages/backend/.env.example packages/backend/.env
docker compose up --build
```

完全なセットアップについては[はじめに](../getting-started/installation.md)を参照し、各レシピの特定の実行手順についてはそのページを確認してください。
