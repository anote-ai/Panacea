# Panacea OpenAI相容的API閘道

這個食譜解釋了如何將任何基於OpenAI SDK構建的工具指向Panacea，而不需要任何代碼更改，同時仍然可以訪問Panacea特定的RAG擴展，如基於文件的資料來源。

## 您將學到什麼

- 如何使用`AnoteOpenAI`來鏡像真實的`openai.OpenAI`客戶端介面
- 如何上傳文件並通過類似聊天完成的API獲取基於文件的答案
- 如何通過伺服器發送事件（SSE）進行串流，類似OpenAI的風格
- Panacea特定的擴展（`anote_sources`，`anote_message_id`）在響應中出現的位置

## 為什麼這很重要

大量現有的工具——LangChain集成、內部腳本、第三方代理框架——都是針對OpenAI SDK的形狀（`client.chat.completions.create(...)`，`client.models.list()`）編寫的。Panacea提供了一個即插即用的客戶端，使用相同的介面，這樣團隊就可以在不重寫其集成代碼的情況下採用Panacea的私有、基於文件的後端，而無需要求每個集成者學習一個定制的Panacea SDK。

## 主要的Panacea文件

| 文件 | 重要性 |
|---|---|
| `Panacea/backend/sdk/anoteai/openai_compat.py` | `AnoteOpenAI`客戶端：`CompletionsClient`，`ModelsClient`，`DocumentsClient`，以及SSE串流解析器 |
| `Panacea/backend/sdk/anoteai/core.py` | 基礎的`PrivateChatbot` SDK類，兼容層包裝了它 |
| `Panacea/backend/sdk/anoteai/handlers/private_handlers.py` | 與原生SDK共享的請求處理 |
| 伺服器路由：`POST /v1/chat/completions`，`GET /v1/models`，`POST /v1/question-answer`，`POST /public/upload` | 客戶端調用的OpenAI形狀（以及一個Panacea特定）的端點 |

## 它是如何工作的

1. 像OpenAI SDK一樣實例化客戶端，但指向您的Panacea後端：

   ```python
   from anoteai.openai_compat import AnoteOpenAI

   client = AnoteOpenAI(
       api_key="your-anote-api-key",       # 或設置 ANOTE_API_KEY
       base_url="http://localhost:5000",    # 或 https://api.anote.ai
   )
   ```

2. 對於基於文件的問答，首先上傳文件——`client.documents.upload(...)`將多部分表單數據發送到`/public/upload`並返回`chat_id`。
3. 以與調用OpenAI SDK相同的方式提問，通過`extra_body`傳遞`chat_id`，以便伺服器知道要檢索哪些文件：

   ```python
   upload_resp = client.documents.upload("path/to/report.pdf")
   chat_id = upload_resp["chat_id"]

   response = client.chat.completions.create(
       model="gpt-4o",
       messages=[{"role": "user", "content": "總結關鍵發現。"}],
       extra_body={"chat_id": chat_id},
   )
   print(response.choices[0].message.content)
   print("來源:", response.anote_sources)
   ```

4. 響應被映射到與真實OpenAI SDK相鏡像的數據類（`ChatCompletion`，`Choice`，`Message`，`Usage`），以及兩個Panacea擴展：`anote_message_id`和`anote_sources`（支持答案的檢索片段/引用）。
5. 傳遞`stream=True`以獲取從`text/event-stream` SSE行解析的`ChatCompletionChunk`對象生成器（每個令牌的`data: {...}`，以`data: [DONE]`結束）——與OpenAI的串流客戶端生成的形狀相同。
6. `client.models.list()`調用`GET /v1/models`以進行模型發現，返回`Model`/`ModelList`對象，與OpenAI SDK一樣。

## 本地運行

從工作區根目錄（`anote/panacea`）：

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

安裝客戶端的一個依賴並設置您的API密鑰：

```bash
pip install requests
export ANOTE_API_KEY=your_api_key_here   # macOS/Linux
set ANOTE_API_KEY=your_api_key_here      # Windows cmd
```

### 最小化演示

```python
from anoteai.openai_compat import AnoteOpenAI

client = AnoteOpenAI(base_url="http://localhost:5000")

# 普通聊天，無文件：
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "法國的首都在哪裡？"}],
)
print(response.choices[0].message.content)

# 串流：
for chunk in client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "數到五。"}],
    stream=True,
):
    for choice in chunk.choices:
        if choice.delta.content:
            print(choice.delta.content, end="", flush=True)
```

## 食譜的注意事項

這個食譜是食譜03的良好補充——它是相同的文件問答/RAG能力，但通過現有的基於OpenAI SDK的工具可以無需修改地使用。值得提醒讀者的是，`DocumentsClient.upload()`/`question_answer()`是基於OpenAI相容核心之上的Panacea特定輔助工具，而不是OpenAI規範的一部分。
