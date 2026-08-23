# Panacea OpenAI 호환 API 게이트웨이

이 레시피는 OpenAI SDK에 맞춰 구축된 도구를 Panacea로 포인팅하는 방법을 설명합니다 — 코드 변경 없이 — 여전히 grounded document sources와 같은 Panacea 전용 RAG 확장에 접근할 수 있습니다.

## 배울 내용

- `AnoteOpenAI`가 실제 `openai.OpenAI` 클라이언트의 인터페이스를 어떻게 반영하는지
- 문서를 업로드하고 채팅 완성 형태의 API를 통해 문서 기반 답변을 얻는 방법
- Server-Sent Events (SSE)에서 스트리밍이 어떻게 작동하는지, OpenAI 스타일로
- Panacea 전용 확장(`anote_sources`, `anote_message_id`)이 응답에서 어디에 나타나는지

## 왜 이것이 중요한가

기존 도구의 상당 부분 — LangChain 통합, 내부 스크립트, 서드파티 에이전트 프레임워크 — 는 OpenAI SDK의 형태(`client.chat.completions.create(...)`, `client.models.list()`)에 맞춰 작성되었습니다. 모든 통합자가 맞춤형 Panacea SDK를 배우도록 요구하기보다는, Panacea는 동일한 인터페이스를 사용하는 드롭인 클라이언트를 제공하여 팀이 통합 코드를 다시 작성하지 않고도 Panacea의 개인 문서 기반 백엔드를 채택할 수 있도록 합니다.

## 주요 Panacea 파일

| 파일 | 중요성 |
|---|---|
| `Panacea/backend/sdk/anoteai/openai_compat.py` | `AnoteOpenAI` 클라이언트: `CompletionsClient`, `ModelsClient`, `DocumentsClient`, 및 SSE 스트림 파서 |
| `Panacea/backend/sdk/anoteai/core.py` | 호환 레이어가 래핑하는 기본 `PrivateChatbot` SDK 클래스 |
| `Panacea/backend/sdk/anoteai/handlers/private_handlers.py` | 네이티브 SDK와 공유되는 요청 처리 |
| 서버 라우트: `POST /v1/chat/completions`, `GET /v1/models`, `POST /v1/question-answer`, `POST /public/upload` | 클라이언트가 호출하는 OpenAI 형태의 (하나의 Panacea 전용) 엔드포인트 |

## 작동 방식

1. OpenAI SDK와 정확히 동일하게 클라이언스를 인스턴스화하되, Panacea 백엔드를 가리킵니다:

   ```python
   from anoteai.openai_compat import AnoteOpenAI

   client = AnoteOpenAI(
       api_key="your-anote-api-key",       # 또는 ANOTE_API_KEY 설정
       base_url="http://localhost:5000",    # 또는 https://api.anote.ai
   )
   ```

2. 문서 기반 Q&A를 위해 먼저 파일을 업로드합니다 — `client.documents.upload(...)`는 `/public/upload`에 multipart 폼 데이터를 게시하고 `chat_id`를 반환합니다.
3. OpenAI SDK를 호출하는 것과 동일한 방식으로 질문을 하며, 서버가 어떤 문서를 검색해야 하는지 알 수 있도록 `extra_body`를 통해 `chat_id`를 전달합니다:

   ```python
   upload_resp = client.documents.upload("path/to/report.pdf")
   chat_id = upload_resp["chat_id"]

   response = client.chat.completions.create(
       model="gpt-4o",
       messages=[{"role": "user", "content": "주요 발견 사항을 요약해 주세요."}],
       extra_body={"chat_id": chat_id},
   )
   print(response.choices[0].message.content)
   print("출처:", response.anote_sources)
   ```

4. 응답은 실제 OpenAI SDK(`ChatCompletion`, `Choice`, `Message`, `Usage`)를 반영하는 데이터 클래스에 매핑되며, 두 개의 Panacea 확장인 `anote_message_id`와 `anote_sources`(답변을 뒷받침하는 검색된 청크/인용)가 포함됩니다.
5. `stream=True`를 전달하여 `text/event-stream` SSE 라인에서 파싱된 `ChatCompletionChunk` 객체의 생성기를 가져옵니다 (`data: {...}`는 토큰당, `data: [DONE]`으로 종료됨) — OpenAI의 스트리밍 클라이언트가 생성하는 동일한 형태입니다.
6. `client.models.list()`는 모델 검색을 위해 `GET /v1/models`를 호출하며, OpenAI SDK와 동일한 `Model`/`ModelList` 객체를 반환합니다.

## 로컬에서 실행하기

작업 공간 루트(`anote/panacea`)에서:

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

클라이언트의 하나의 종속성을 설치하고 API 키를 설정합니다:

```bash
pip install requests
export ANOTE_API_KEY=your_api_key_here   # macOS/Linux
set ANOTE_API_KEY=your_api_key_here      # Windows cmd
```

### 최소한의 워크스루

```python
from anoteai.openai_compat import AnoteOpenAI

client = AnoteOpenAI(base_url="http://localhost:5000")

# 문서 없이 일반 채팅:
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "프랑스의 수도는 어디인가요?"}],
)
print(response.choices[0].message.content)

# 스트리밍:
for chunk in client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "하나부터 다섯까지 세어보세요."}],
    stream=True,
):
    for choice in chunk.choices:
        if choice.delta.content:
            print(choice.delta.content, end="", flush=True)
```

## 요리책을 위한 노트

이 레시피는 레시피 03에 좋은 보완이 됩니다 — 동일한 문서 Q&A/RAG 기능이지만, 기존 OpenAI-SDK 기반 도구가 수정 없이 사용할 수 있는 인터페이스를 통해 노출됩니다. `DocumentsClient.upload()`/`question_answer()`가 OpenAI 호환 코어 위에 레이어된 Panacea 전용 헬퍼라는 점을 독자에게 강조할 가치가 있습니다.
