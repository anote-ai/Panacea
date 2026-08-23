# Panacea 다채널 메시징 봇

이 레시피는 Panacea의 채팅 운영 스타일 통합을 설명합니다: 사용자가 이미 사용하는 메시징 앱에서 코딩 질문을 할 수 있도록 해주는 독립형 Slack, SMS 및 WhatsApp 봇입니다.

## 배울 내용

- 세 개의 봇 모두에 걸쳐 공유되는 디자인 패턴: 수신 → LLM 호출 → 채널의 문자 제한에 맞게 잘라내기 → 응답
- Slack 봇이 스레딩을 처리하고 "생각 중…" 자리 표시자를 제자리에서 수정하는 방법
- SMS/WhatsApp 봇이 Twilio의 TwiML을 사용하여 동기적으로 응답하는 방법
- 이러한 봇을 확장하기 전에 알아야 할 현재의 아키텍처 격차

## 왜 이것이 중요한가

모든 사용자가 질문을 하기 위해 웹 UI나 IDE를 열고 싶어하는 것은 아닙니다 — 채팅 운영 스타일 통합은 사람들이 이미 있는 곳에서 그들을 만납니다. 각 봇은 독립적으로 배포 가능한 작은 Flask 서비스이므로 팀은 Panacea의 나머지 스택을 설정하지 않고도 필요한 채널만 실행할 수 있습니다(예: Slack만).

## 주요 Panacea 파일

| 파일 | 중요성 |
|---|---|
| `Panacea/packages/bots/slack/app.py` | Slack Bolt 앱; 소켓 모드 또는 HTTP 웹훅 지원; 제자리에서 업데이트되는 스레드형 "생각 중…" 자리 표시자 |
| `Panacea/packages/bots/sms/app.py` | Twilio SMS 웹훅 핸들러 (`MessagingResponse`/TwiML) |
| `Panacea/packages/bots/whatsapp/app.py` | Twilio WhatsApp 샌드박스 웹훅 핸들러 |
| `Panacea/packages/bots/{slack,sms,whatsapp}/.env.example` | 채널별로 필요한 자격 증명 |

## 작동 방식

1. **Slack** (`slack/app.py`): `app_mention` 이벤트를 수신합니다. `extract_query()`는 메시지 텍스트에서 `<@BOT_ID>` 언급을 제거합니다. 즉시 `_Anote is thinking…_` 자리 표시자 메시지를 게시한 후, 백그라운드 스레드에서 LLM 호출을 실행하고 `client.chat_update(...)`를 통해 제자리에서 해당 자리 표시자를 수정하거나, 자리 표시자 게시물이 실패한 경우 새 스레드형 응답을 보냅니다.
2. **SMS** (`sms/app.py`): Twilio는 각 수신 텍스트를 `/sms`로 폼 데이터(`Body`, `From`)로 POST합니다. 핸들러는 LLM을 동기적으로 호출하고 응답과 함께 `MessagingResponse` (TwiML)를 반환합니다 — Twilio는 이를 후속 텍스트로 전달합니다.
3. **WhatsApp** (`whatsapp/app.py`): SMS와 동일한 TwiML 패턴으로, 전화번호 대신 Twilio의 WhatsApp 샌드박스 웹훅에 연결됩니다.
4. 세 개의 봇 모두 **Anthropic API를 직접 호출**합니다 (`anthropic.Anthropic(...).messages.create(...)`) — Anote를 코딩 도우미로 설명하는 공유 시스템 프롬프트를 사용합니다. 현재 Panacea의 자체 백엔드를 통해 프록시하지 않으므로 RAG/문서 기반, 크레딧 미터링 또는 레시피 03/04/08의 다중 에이전트 오케스트레이션을 받지 않습니다.
5. 응답은 전송 전에 각 채널의 제한으로 잘립니다: Slack 2900자, SMS/WhatsApp 1600자, 잘린 경우 잘림 알림이 추가됩니다.

### 알아야 할 아키텍처 격차

이 봇들이 Panacea의 백엔드를 통해 라우팅하는 대신 Anthropic을 직접 호출하기 때문에, Slack/SMS/WhatsApp 사용자는 현재 Panacea에 업로드한 문서에 기반한 질문을 할 수 없으며, 그들의 사용은 레시피 08의 크레딧 시스템을 통해 미터링되지 않습니다. 웹 UI와 채널 동등성을 원한다면, 자연스러운 다음 단계는 직접 `anthropic_client.messages.create(...)` 호출을 Panacea의 `/v1/chat/completions` 요청으로 교체하는 것입니다(레시피 07의 OpenAI 호환 게이트웨이) 이로 인해 이러한 봇은 RAG, 오케스트레이션 및 청구를 무료로 상속받습니다.

## 로컬에서 실행하기

각 봇은 독립적입니다 — 필요한 것만 설치하고 실행하세요.

### Slack

```bash
cd Panacea/packages/bots/slack
pip install -r requirements.txt
cp .env.example .env   # SLACK_BOT_TOKEN, SLACK_SIGNING_SECRET, ANTHROPIC_API_KEY 입력
python app.py
```

소켓 모드에서 실행하려면 `.env`에 `SLACK_APP_TOKEN`을 설정하세요(공개 URL 필요 없음); 그렇지 않으면 `PORT`(기본 3000)에서 HTTP를 제공하며 Slack의 Events API 웹훅이 `POST /slack/events`를 가리키도록 기대합니다.

### SMS

```bash
cd Panacea/packages/bots/sms
pip install -r requirements.txt
cp .env.example .env   # ANTHROPIC_API_KEY 입력
python app.py
```

Twilio 전화번호의 SMS 웹훅을 `POST https://<your-host>/sms`로 구성하세요(기본 포트 3001).

### WhatsApp

```bash
cd Panacea/packages/bots/whatsapp
pip install -r requirements.txt
cp .env.example .env   # ANTHROPIC_API_KEY 입력
python app.py
```

Twilio WhatsApp 샌드박스 웹훅을 이 서비스의 `POST /whatsapp`를 가리키도록 구성하세요.

각 봇은 또한 빠른 생존 확인을 위한 `GET /health`를 노출합니다.

## 요리책을 위한 노트

이것은 "Panacea 확장" 레시피로 좋습니다: 독자는 직접 Anthropic 버전이 몇 분 안에 작동하는 것을 보고, 위의 아키텍처 격차 노트를 따라 Panacea의 백엔드를 통해 연결하여 기반이 있는, 미터링된 응답을 받을 수 있습니다.
