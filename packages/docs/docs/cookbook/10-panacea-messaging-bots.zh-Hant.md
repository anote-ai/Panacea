# Panacea 多通道消息機器人

本食譜解釋了 Panacea 的聊天操作風格整合：獨立的 Slack、SMS 和 WhatsApp 機器人，讓用戶可以從他們已經使用的消息應用程式中詢問編程問題。

## 您將學到什麼

- 三個機器人之間的共享設計模式：接收 → 調用 LLM → 修剪至通道的字符限制 → 回覆
- Slack 機器人如何處理線程並在原地編輯「思考中…」佔位符
- SMS/WhatsApp 機器人如何使用 Twilio 的 TwiML 同步回覆
- 在擴展這些機器人之前值得了解的當前架構差距

## 為什麼這很重要

並非每個用戶都想打開網頁 UI 或 IDE 來詢問問題——聊天操作風格的整合讓人們在他們已經存在的地方進行互動。每個機器人都是一個小型的、獨立可部署的 Flask 服務，因此團隊可以僅運行他們所需的通道（例如僅 Slack），而無需啟動其餘的 Panacea 堆棧。

## 主要的 Panacea 檔案

| 檔案 | 為什麼重要 |
|---|---|
| `Panacea/packages/bots/slack/app.py` | Slack Bolt 應用程式；支持 Socket 模式或 HTTP webhook；線程中的「思考中…」佔位符在原地更新 |
| `Panacea/packages/bots/sms/app.py` | Twilio SMS webhook 處理器 (`MessagingResponse`/TwiML) |
| `Panacea/packages/bots/whatsapp/app.py` | Twilio WhatsApp 沙盒 webhook 處理器 |
| `Panacea/packages/bots/{slack,sms,whatsapp}/.env.example` | 每個通道所需的憑證 |

## 它是如何運作的

1. **Slack** (`slack/app.py`): 監聽 `app_mention` 事件。`extract_query()` 從消息文本中剝離 `<@BOT_ID>` 提及。它立即發佈一條 `_Anote 正在思考…_` 佔位符消息，然後在背景線程上運行 LLM 調用，並通過 `client.chat_update(...)` 在原地編輯該佔位符，或者如果佔位符發佈失敗，則發送一條新的線程回覆。
2. **SMS** (`sms/app.py`): Twilio 將每條進來的文本以表單數據 (`Body`, `From`) POST 到 `/sms`。處理器同步調用 LLM 並返回一個 `MessagingResponse` (TwiML) 作為回覆——Twilio 將其作為後續文本發送。
3. **WhatsApp** (`whatsapp/app.py`): 與 SMS 相同的 TwiML 模式，連接到 Twilio 的 WhatsApp 沙盒 webhook，而不是電話號碼。
4. 三者都直接調用 **Anthropic API** (`anthropic.Anthropic(...).messages.create(...)`)，使用共享的系統提示將 Anote 描述為編程助手——它們目前不通過 Panacea 的後端代理，因此無法獲得 RAG/文檔基礎、信用計量或來自食譜 03/04/08 的多代理協調。
5. 回應在發送之前會修剪至每個通道的限制：Slack 2900 字符，SMS/WhatsApp 1600 字符，若被截斷則附加截斷通知。

### 需要了解的架構差距

由於這些機器人直接調用 Anthropic，而不是通過 Panacea 的後端路由，Slack/SMS/WhatsApp 用戶目前無法詢問基於他們上傳到 Panacea 的文檔的問題，並且他們的使用情況不會通過食譜 08 的信用系統進行計量。如果您希望與網頁 UI 保持通道一致，下一步自然是將直接的 `anthropic_client.messages.create(...)` 調用替換為對 Panacea 自己的 `/v1/chat/completions` 的請求（食譜 07 的 OpenAI 兼容網關），這樣這些機器人就可以繼承 RAG、協調和免費計費。

## 本地運行

每個機器人都是獨立的——僅安裝和運行您所需的機器人。

### Slack

```bash
cd Panacea/packages/bots/slack
pip install -r requirements.txt
cp .env.example .env   # 填寫 SLACK_BOT_TOKEN, SLACK_SIGNING_SECRET, ANTHROPIC_API_KEY
python app.py
```

在 `.env` 中設置 `SLACK_APP_TOKEN` 以在 Socket 模式下運行（不需要公共 URL）；否則，它在 `PORT`（默認 3000）上提供 HTTP，並期望 Slack 的事件 API webhook 指向 `POST /slack/events`。

### SMS

```bash
cd Panacea/packages/bots/sms
pip install -r requirements.txt
cp .env.example .env   # 填寫 ANTHROPIC_API_KEY
python app.py
```

將您的 Twilio 電話號碼的 SMS webhook 配置為 `POST https://<your-host>/sms`（默認端口 3001）。

### WhatsApp

```bash
cd Panacea/packages/bots/whatsapp
pip install -r requirements.txt
cp .env.example .env   # 填寫 ANTHROPIC_API_KEY
python app.py
```

將您的 Twilio WhatsApp 沙盒 webhook 配置為指向此服務的 `POST /whatsapp`。

每個機器人還提供 `GET /health` 以進行快速存活檢查。

## 食譜的注意事項

這是一個很好的「擴展 Panacea」食譜：讀者可以在幾分鐘內看到直接到 Anthropic 的版本運行，然後根據上述架構差距說明將其連接到 Panacea 的後端，以獲得基於文檔的、有計量的答案。
