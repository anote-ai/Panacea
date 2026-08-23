# Panacea 多渠道消息机器人

本食谱解释了 Panacea 的聊天操作风格集成：独立的 Slack、SMS 和 WhatsApp 机器人，让用户可以通过他们已经使用的消息应用程序提问编码问题。

## 您将学到什么

- 三个机器人的共享设计模式：接收 → 调用 LLM → 修剪到频道的字符限制 → 回复
- Slack 机器人如何处理线程并在原地编辑“思考中……”占位符
- SMS/WhatsApp 机器人如何使用 Twilio 的 TwiML 同步回复
- 在扩展这些机器人之前值得了解的当前架构差距

## 这很重要的原因

并不是每个用户都想打开网页 UI 或 IDE 来提问——聊天操作风格的集成让人们在他们已经存在的地方进行交互。每个机器人都是一个小型的、独立可部署的 Flask 服务，因此团队可以仅运行他们所需的频道（例如，仅 Slack），而无需启动其余的 Panacea 堆栈。

## 关键的 Panacea 文件

| 文件 | 重要性 |
|---|---|
| `Panacea/packages/bots/slack/app.py` | Slack Bolt 应用；支持 Socket 模式或 HTTP webhook；线程中的“思考中……”占位符在原地更新 |
| `Panacea/packages/bots/sms/app.py` | Twilio SMS webhook 处理程序 (`MessagingResponse`/TwiML) |
| `Panacea/packages/bots/whatsapp/app.py` | Twilio WhatsApp 沙盒 webhook 处理程序 |
| `Panacea/packages/bots/{slack,sms,whatsapp}/.env.example` | 每个频道所需的凭据 |

## 工作原理

1. **Slack** (`slack/app.py`): 监听 `app_mention` 事件。`extract_query()` 从消息文本中剥离 `<@BOT_ID>` 提及。它立即发布一个 `_Anote 正在思考中…_` 占位符消息，然后在后台线程上运行 LLM 调用，并通过 `client.chat_update(...)` 在原地编辑该占位符，或者如果占位符帖子失败，则发送一个新的线程回复。
2. **SMS** (`sms/app.py`): Twilio 将每个传入文本以表单数据 (`Body`, `From`) 的形式 POST 到 `/sms`。处理程序同步调用 LLM 并返回一个 `MessagingResponse` (TwiML) 作为回复——Twilio 将其作为后续文本发送。
3. **WhatsApp** (`whatsapp/app.py`): 与 SMS 相同的 TwiML 模式，连接到 Twilio 的 WhatsApp 沙盒 webhook，而不是电话号码。
4. 三个机器人直接调用 **Anthropic API** (`anthropic.Anthropic(...).messages.create(...)`)，使用共享的系统提示将 Anote 描述为编码助手——它们目前不通过 Panacea 的后端代理，因此无法获得 RAG/文档基础、信用计量或来自食谱 03/04/08 的多代理协调。
5. 在发送之前，回复会被修剪到每个频道的限制：Slack 2900 个字符，SMS/WhatsApp 1600 个字符，如果被截断，则附加截断通知。

### 需要了解的架构差距

由于这些机器人直接调用 Anthropic，而不是通过 Panacea 的后端路由，因此 Slack/SMS/WhatsApp 用户目前无法提出基于他们上传到 Panacea 的文档的问题，并且他们的使用不通过食谱 08 的信用系统进行计量。如果您希望与网页 UI 保持一致，下一步自然是将直接的 `anthropic_client.messages.create(...)` 调用替换为对 Panacea 自己的 `/v1/chat/completions`（食谱 07 的 OpenAI 兼容网关）的请求，以便这些机器人继承 RAG、协调和免费计费。

## 本地运行

每个机器人都是独立的——仅安装和运行您需要的机器人。

### Slack

```bash
cd Panacea/packages/bots/slack
pip install -r requirements.txt
cp .env.example .env   # 填写 SLACK_BOT_TOKEN, SLACK_SIGNING_SECRET, ANTHROPIC_API_KEY
python app.py
```

在 `.env` 中设置 `SLACK_APP_TOKEN` 以在 Socket 模式下运行（不需要公共 URL）；否则，它在 `PORT`（默认 3000）上提供 HTTP，并期望 Slack 的事件 API webhook 指向 `POST /slack/events`。

### SMS

```bash
cd Panacea/packages/bots/sms
pip install -r requirements.txt
cp .env.example .env   # 填写 ANTHROPIC_API_KEY
python app.py
```

将您的 Twilio 电话号码的 SMS webhook 配置为 `POST https://<your-host>/sms`（默认端口 3001）。

### WhatsApp

```bash
cd Panacea/packages/bots/whatsapp
pip install -r requirements.txt
cp .env.example .env   # 填写 ANTHROPIC_API_KEY
python app.py
```

将您的 Twilio WhatsApp 沙盒 webhook 配置为指向此服务上的 `POST /whatsapp`。

每个机器人还公开 `GET /health` 以进行快速存活检查。

## 食谱的注意事项

这是一个很好的“扩展 Panacea”食谱：读者可以在几分钟内看到直接到 Anthropic 的版本工作，然后按照上面的架构差距说明通过 Panacea 的后端进行连接，以获得有基础的、计量的答案。
