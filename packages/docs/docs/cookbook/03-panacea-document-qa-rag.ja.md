# Panacea ドキュメント Q&A + RAG

このレシピは、Panacea がプライベートドキュメントの質問応答をリトリーバル拡張生成 (RAG) で構築する方法を説明します。

## 学べること

- Panacea がドキュメントを取り込み、検索可能なテキストとして保存する方法
- バックエンドが質問に対して関連するチャンクを取得する方法
- システムが埋め込みとドキュメントソースを使用して回答を根拠づける方法
- Q&A フィードバックがどのようにキャプチャされ、将来の応答を改善するか

## なぜこれが重要か

Panacea は、チームがプライベートドキュメントに質問をする際に、サードパーティのチャットサービスに送信することなく行えるように設計されています。ワークフローは次のとおりです：

1. ドキュメントをアップロード
2. コンテンツをチャンク化し、埋め込む
3. ユーザーのクエリに対して関連するチャンクを取得
4. 引用を用いて LLM で回答
5. 品質向上のためにフィードバックをキャプチャ

## 主要な Panacea ファイル

| ファイル | 重要な理由 |
|---|---|
| `Panacea/backend/api_endpoints/documents/handler.py` | ドキュメントのアップロードと取り込みの API ルート |
| `Panacea/backend/database/db.py` | ドキュメントの保存と取得の SQL ロジック |
| `Panacea/backend/database/qa_feedback.py` | ドキュメント Q&A のフィードバックキャプチャ |
| `Panacea/backend/agents/multi_agent_system.py` | マルチエージェントワークフローで使用されるドキュメント取得エージェント |

## 仕組み

- ドキュメントはバックエンドを通じてアップロードされ、`documents.document_text` に保存されます。
- システムは大きなドキュメントをチャンク化し、高速検索のためのメタデータを作成します。
- ユーザーが質問をすると、Panacea は最適なチャンクを取得するために 1 つ以上の専門エージェントを選択し、その後回答を生成します。
- 結果にはソースの引用が含まれており、ユーザーは回答を元のドキュメントに遡ることができます。
- フィードバック信号は `qa_feedback` に記録され、将来の品質向上を可能にします。

## ローカルで実行する

ワークスペースのルートから (`anote/panacea`)：

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

これにより、バックエンド、ウェブアプリ、MySQL、Redis、Tika が起動します。

もしレシピフォルダ内にいる場合は、次のようにします：

```bash
cd ../../../Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

`http://localhost:3000` を開いて Panacea のウェブ UI を使用します。ドキュメントのアップロードは、必要なフォームフィールド `chat_id` と `files[]` を持つバックエンドルート `POST /ingest-pdf` によって処理されます。

アップロードコマンドの例：

```bash
curl -X POST http://localhost:5000/ingest-pdf \
  -F chat_id=1 \
  -F "files[]=@./path/to/document.pdf"
```

### 最小限のアップロード手順

1. リポジトリのルートから Panacea を起動します：

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

2. 別のターミナルで、単一のテキストまたは PDF ドキュメントをアップロードします：

```bash
curl -X POST http://localhost:5000/ingest-pdf \
  -F chat_id=1 \
  -F "files[]=@./Cookbook/recipes/03-panacea-document-qa-rag/data/sample-doc.txt"
```

3. バックエンドが成功した `Document Uploaded` レスポンスを返すことを確認します。

4. `http://localhost:3000` でウェブ UI を使用し、同じチャットセッションを選択してアップロードしたドキュメントに関する質問をします。

アップロード後に API を直接テストしたい場合は、UI またはデータベースでチャットセッション ID を見つけ、アプリのチャットフローを通じて質問を送信します。Panacea は関連するチャンクを取得し、根拠のある回答を生成します。

## クックブックのためのノート

このレシピは、Panacea がプライベートな知識作業をどのようにサポートするかを説明するクックブックエントリに最適です。これは一行のスクリプトよりも概念的であり、実際の価値はドキュメントの取り込みと取得のアーキテクチャを理解することにあります。
