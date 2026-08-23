# Панасея OpenAI-совместимый API шлюз

Этот рецепт объясняет, как направить любой инструмент, созданный с использованием OpenAI SDK, на Панасею — без изменений в коде — при этом получая доступ к специфическим расширениям RAG Панасеи, таким как источники документов.

## Что вы узнаете

- Как `AnoteOpenAI` отражает интерфейс реального клиента `openai.OpenAI`
- Как загружать документы и получать ответы, основанные на документах, через API, оформленный как chat-completions
- Как работает потоковая передача через события, отправляемые сервером (SSE), в стиле OpenAI
- Где появляются специфические для Панасеи расширения (`anote_sources`, `anote_message_id`) в ответе

## Почему это важно

Огромное количество существующих инструментов — интеграции LangChain, внутренние скрипты, фреймворки сторонних агентов — написано с учетом структуры OpenAI SDK (`client.chat.completions.create(...)`, `client.models.list()`). Вместо того чтобы просить каждого интегратора изучать индивидуальный SDK Панасеи, Панасея предоставляет клиент, который использует тот же интерфейс, так что команды могут использовать частный, основанный на документах бэкенд Панасеи без переписывания своего интеграционного кода.

## Ключевые файлы Панасеи

| Файл | Почему это важно |
|---|---|
| `Panacea/backend/sdk/anoteai/openai_compat.py` | Клиент `AnoteOpenAI`: `CompletionsClient`, `ModelsClient`, `DocumentsClient` и парсер потока SSE |
| `Panacea/backend/sdk/anoteai/core.py` | Основной класс SDK `PrivateChatbot`, который оборачивает совместимый слой |
| `Panacea/backend/sdk/anoteai/handlers/private_handlers.py` | Обработка запросов, общая с нативным SDK |
| Маршруты сервера: `POST /v1/chat/completions`, `GET /v1/models`, `POST /v1/question-answer`, `POST /public/upload` | Эндпоинты в стиле OpenAI (и один специфичный для Панасеи), которые вызывает клиент |

## Как это работает

1. Создайте экземпляр клиента точно так же, как и OpenAI SDK, но указывая на ваш бэкенд Панасеи:

   ```python
   from anoteai.openai_compat import AnoteOpenAI

   client = AnoteOpenAI(
       api_key="your-anote-api-key",       # или установите ANOTE_API_KEY
       base_url="http://localhost:5000",    # или https://api.anote.ai
   )
   ```

2. Для вопросов и ответов, основанных на документах, сначала загрузите файлы — `client.documents.upload(...)` отправляет многокомпонентные данные формы на `/public/upload` и возвращает `chat_id`.
3. Задайте вопрос так же, как вы бы вызвали OpenAI SDK, передавая `chat_id` через `extra_body`, чтобы сервер знал, какие документы извлекать:

   ```python
   upload_resp = client.documents.upload("path/to/report.pdf")
   chat_id = upload_resp["chat_id"]

   response = client.chat.completions.create(
       model="gpt-4o",
       messages=[{"role": "user", "content": "Подведите итоги ключевых выводов."}],
       extra_body={"chat_id": chat_id},
   )
   print(response.choices[0].message.content)
   print("Источники:", response.anote_sources)
   ```

4. Ответ отображается в дата-классах, которые отражают реальный OpenAI SDK (`ChatCompletion`, `Choice`, `Message`, `Usage`), плюс два расширения Панасеи: `anote_message_id` и `anote_sources` (извлеченные фрагменты/цитаты, поддерживающие ответ).
5. Передайте `stream=True`, чтобы получить генератор объектов `ChatCompletionChunk`, разобранных из строк `text/event-stream` SSE (`data: {...}` для каждого токена, завершенных `data: [DONE]`) — такая же структура, которую производит потоковый клиент OpenAI.
6. `client.models.list()` вызывает `GET /v1/models` для обнаружения моделей, возвращая объекты `Model`/`ModelList`, как и OpenAI SDK.

## Запустите локально

Из корня рабочего пространства (`anote/panacea`):

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

Установите единую зависимость клиента и установите ваш API ключ:

```bash
pip install requests
export ANOTE_API_KEY=your_api_key_here   # macOS/Linux
set ANOTE_API_KEY=your_api_key_here      # Windows cmd
```

### Минимальная инструкция

```python
from anoteai.openai_compat import AnoteOpenAI

client = AnoteOpenAI(base_url="http://localhost:5000")

# Обычный чат, без документов:
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Какова столица Франции?"}],
)
print(response.choices[0].message.content)

# Потоковая передача:
for chunk in client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Сосчитайте до пяти."}],
    stream=True,
):
    for choice in chunk.choices:
        if choice.delta.content:
            print(choice.delta.content, end="", flush=True)
```

## Заметки для кулинарной книги

Этот рецепт является хорошим дополнением к рецепту 03 — это та же возможность вопросов и ответов/RAG по документам, но представленная через интерфейс, который существующие инструменты на основе OpenAI-SDK могут использовать без изменений. Стоит отметить читателям, что `DocumentsClient.upload()`/`question_answer()` являются специфическими для Панасеи помощниками, наложенными на совместимую основу OpenAI, а не частью самой спецификации OpenAI.
