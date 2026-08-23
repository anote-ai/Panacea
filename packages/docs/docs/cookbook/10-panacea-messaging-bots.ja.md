# Panacea マルチチャネルメッセージングボット

このレシピは、Panaceaのチャットオプスタイルの統合について説明します：ユーザーが既に使用しているメッセージングアプリからコーディングの質問をすることを可能にする、スタンドアロンのSlack、SMS、およびWhatsAppボットです。

## 学べること

- 3つのボット全体に共通するデザインパターン：受信 → LLMを呼び出す → チャンネルの文字制限に合わせてトリム → 返信
- Slackボットがスレッド処理をどのように行い、「考え中…」のプレースホルダーをその場で編集するか
- SMS/WhatsAppボットがTwilioのTwiMLを使用してどのように同期的に返信するか
- これらのボットを拡張する前に知っておくべき現在のアーキテクチャのギャップ

## なぜこれが重要か

すべてのユーザーが質問をするためにウェブUIやIDEを開きたいわけではありません — チャットオプスタイルの統合は、人々が既にいる場所で彼らに対応します。各ボットは小さな独立してデプロイ可能なFlaskサービスであるため、チームは必要なチャンネル（例：Slackのみ）を実行でき、Panaceaのスタック全体を立ち上げる必要はありません。

## 主要なPanaceaファイル

| ファイル | 重要な理由 |
|---|---|
| `Panacea/packages/bots/slack/app.py` | Slack Boltアプリ; ソケットモードまたはHTTPウェブフックをサポート; スレッド化された「考え中…」プレースホルダーがその場で更新される |
| `Panacea/packages/bots/sms/app.py` | Twilio SMSウェブフックハンドラー（`MessagingResponse`/TwiML） |
| `Panacea/packages/bots/whatsapp/app.py` | Twilio WhatsAppサンドボックスウェブフックハンドラー |
| `Panacea/packages/bots/{slack,sms,whatsapp}/.env.example` | チャンネルごとの必要な認証情報 |

## 仕組み

1. **Slack** (`slack/app.py`): `app_mention`イベントをリッスンします。`extract_query()`はメッセージテキストから`<@BOT_ID>`のメンションを取り除きます。すぐに`_Anote is thinking…_`のプレースホルダーメッセージを投稿し、その後バックグラウンドスレッドでLLM呼び出しを実行し、`client.chat_update(...)`を介してその場でプレースホルダーを編集するか、プレースホルダーポストが失敗した場合は新しいスレッド返信を送信します。
2. **SMS** (`sms/app.py`): Twilioは各受信テキストを`/sms`にフォームデータ（`Body`, `From`）としてPOSTします。ハンドラーはLLMを同期的に呼び出し、返信を含む`MessagingResponse`（TwiML）を返します — Twilioはそれをフォローアップテキストとして配信します。
3. **WhatsApp** (`whatsapp/app.py`): SMSと同じTwiMLパターンで、電話番号の代わりにTwilioのWhatsAppサンドボックスウェブフックに接続されています。
4. すべてのボットは**Anthropic APIを直接呼び出します**（`anthropic.Anthropic(...).messages.create(...)`）で、Anoteをコーディングアシスタントとして説明する共有システムプロンプトを使用します — 現在、Panaceaのバックエンドを介してプロキシされていないため、RAG/ドキュメントグラウンディング、クレジットメータリング、またはレシピ03/04/08からのマルチエージェントオーケストレーションは受けられません。
5. 返信は送信前に各チャンネルの制限にトリムされます：Slack 2900文字、SMS/WhatsApp 1600文字、それぞれカットされた場合は切り捨て通知が追加されます。

### 知っておくべきアーキテクチャのギャップ

これらのボットはAnthropicを直接呼び出すため、Slack/SMS/WhatsAppユーザーは現在、Panaceaにアップロードしたドキュメントに基づいて質問をすることができず、彼らの使用はレシピ08のクレジットシステムを通じてメータリングされていません。ウェブUIとのチャンネルの均一性を望む場合、次の自然なステップは、直接の`anthropic_client.messages.create(...)`呼び出しをPanaceaの独自の`/v1/chat/completions`（レシピ07のOpenAI互換ゲートウェイ）へのリクエストに置き換えることです。これにより、これらのボットはRAG、オーケストレーション、および請求を無料で継承します。

## ローカルで実行する

各ボットは独立しており、必要なものだけをインストールして実行します。

### Slack

```bash
cd Panacea/packages/bots/slack
pip install -r requirements.txt
cp .env.example .env   # SLACK_BOT_TOKEN、SLACK_SIGNING_SECRET、ANTHROPIC_API_KEYを入力
python app.py
```

ソケットモードで実行するには、`.env`に`SLACK_APP_TOKEN`を設定します（パブリックURLは不要）。そうでない場合は、`PORT`（デフォルト3000）でHTTPを提供し、SlackのEvents APIウェブフックが`POST /slack/events`を指すことを期待します。

### SMS

```bash
cd Panacea/packages/bots/sms
pip install -r requirements.txt
cp .env.example .env   # ANTHROPIC_API_KEYを入力
python app.py
```

Twilioの電話番号のSMSウェブフックを`POST https://<your-host>/sms`（デフォルトポート3001）に設定します。

### WhatsApp

```bash
cd Panacea/packages/bots/whatsapp
pip install -r requirements.txt
cp .env.example .env   # ANTHROPIC_API_KEYを入力
python app.py
```

TwilioのWhatsAppサンドボックスウェブフックをこのサービスの`POST /whatsapp`にポイントするように設定します。

各ボットはまた、迅速な生存確認のために`GET /health`を公開しています。

## クックブックのためのノート

これは「Panaceaを拡張する」ための良いレシピです：読者は、直接Anthropicバージョンが数分で動作するのを見た後、上記のアーキテクチャのギャップノートに従って、Panaceaのバックエンドを介してそれを接続し、グラウンドされたメータリングされた回答を得ることができます。
