# Panacea OpenAI互換APIゲートウェイ

このレシピでは、OpenAI SDKに対して構築された任意のツールをPanaceaに向ける方法を説明します — コードの変更なしで — それでも、基盤となる文書ソースのようなPanacea特有のRAG拡張にアクセスできます。

## 学べること

- `AnoteOpenAI`が実際の`openai.OpenAI`クライアントのインターフェースをどのようにミラーリングするか
- 文書をアップロードし、チャット完了形式のAPIを通じて文書に基づいた回答を得る方法
- サーバー送信イベント（SSE）を介したストリーミングの動作
- Panacea特有の拡張（`anote_sources`、`anote_message_id`）がレスポンスにどのように現れるか

## なぜこれが重要か

既存のツールの多く — LangChain統合、内部スクリプト、サードパーティエージェントフレームワーク — はOpenAI SDKの形状（`client.chat.completions.create(...)`、`client.models.list()`）に対して書かれています。すべての統合者に特注のPanacea SDKを学ばせるのではなく、Panaceaは同じインターフェースを話すドロップインクライアントを提供するため、チームは統合コードを再記述することなくPanaceaのプライベートな文書に基づいたバックエンドを採用できます。

## 主要なPanaceaファイル

| ファイル | 重要な理由 |
|---|---|
| `Panacea/backend/sdk/anoteai/openai_compat.py` | `AnoteOpenAI`クライアント: `CompletionsClient`、`ModelsClient`、`DocumentsClient`、およびSSEストリームパーサー |
| `Panacea/backend/sdk/anoteai/core.py` | 互換レイヤーがラップする基盤となる`PrivateChatbot` SDKクラス |
| `Panacea/backend/sdk/anoteai/handlers/private_handlers.py` | ネイティブSDKと共有されるリクエスト処理 |
| サーバールート: `POST /v1/chat/completions`、`GET /v1/models`、`POST /v1/question-answer`、`POST /public/upload` | クライアントが呼び出すOpenAI形式（および1つのPanacea特有）のエンドポイント |

## 仕組み

1. OpenAI SDKと同じようにクライアントをインスタンス化しますが、Panaceaバックエンドを指します：

   ```python
   from anoteai.openai_compat import AnoteOpenAI

   client = AnoteOpenAI(
       api_key="your-anote-api-key",       # またはANOTE_API_KEYを設定
       base_url="http://localhost:5000",    # またはhttps://api.anote.ai
   )
   ```

2. 文書に基づいたQ&Aのために、最初にファイルをアップロードします — `client.documents.upload(...)`は`/public/upload`にマルチパートフォームデータを投稿し、`chat_id`を返します。
3. OpenAI SDKを呼び出すのと同じ方法で質問をします。`chat_id`を`extra_body`を通じて渡し、サーバーがどの文書を取得するかを知ることができます：

   ```python
   upload_resp = client.documents.upload("path/to/report.pdf")
   chat_id = upload_resp["chat_id"]

   response = client.chat.completions.create(
       model="gpt-4o",
       messages=[{"role": "user", "content": "主な発見を要約してください。"}],
       extra_body={"chat_id": chat_id},
   )
   print(response.choices[0].message.content)
   print("ソース:", response.anote_sources)
   ```

4. レスポンスは、実際のOpenAI SDKをミラーリングするデータクラス（`ChatCompletion`、`Choice`、`Message`、`Usage`）にマッピングされ、さらに2つのPanacea拡張（`anote_message_id`と`anote_sources`、回答を支える取得されたチャンク/引用）が含まれます。
5. `stream=True`を渡すことで、`text/event-stream` SSE行から解析された`ChatCompletionChunk`オブジェクトのジェネレーターを取得します（トークンごとに`data: {...}`、`data: [DONE]`で終了） — OpenAIのストリーミングクライアントが生成するのと同じ形状です。
6. `client.models.list()`は`GET /v1/models`を呼び出し、モデルの発見を行い、OpenAI SDKと同様の`Model`/`ModelList`オブジェクトを返します。

## ローカルで実行する

ワークスペースのルート（`anote/panacea`）から：

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

クライアントの依存関係を1つインストールし、APIキーを設定します：

```bash
pip install requests
export ANOTE_API_KEY=your_api_key_here   # macOS/Linux
set ANOTE_API_KEY=your_api_key_here      # Windows cmd
```

### 最小限のウォークスルー

```python
from anoteai.openai_compat import AnoteOpenAI

client = AnoteOpenAI(base_url="http://localhost:5000")

# 文書なしの通常のチャット:
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "フランスの首都はどこですか？"}],
)
print(response.choices[0].message.content)

# ストリーミング:
for chunk in client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "1から5まで数えてください。"}],
    stream=True,
):
    for choice in chunk.choices:
        if choice.delta.content:
            print(choice.delta.content, end="", flush=True)
```

## クックブックのためのノート

このレシピはレシピ03の良い補完です — 同じ文書Q&A/RAG機能ですが、既存のOpenAI SDKベースのツールが変更なしで利用できるインターフェースを通じて公開されています。`DocumentsClient.upload()`/`question_answer()`は、OpenAI互換のコアの上にレイヤーされたPanacea特有のヘルパーであり、OpenAIの仕様の一部ではないことを読者に注意喚起する価値があります。
