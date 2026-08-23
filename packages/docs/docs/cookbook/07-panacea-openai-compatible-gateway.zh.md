# Panacea OpenAI兼容API网关

本食谱解释了如何将任何针对OpenAI SDK构建的工具指向Panacea，而无需任何代码更改，同时仍然可以访问Panacea特定的RAG扩展，如基础文档源。

## 您将学到什么

- `AnoteOpenAI` 如何镜像真实的 `openai.OpenAI` 客户端接口
- 如何上传文档并通过聊天完成形状的API获取基于文档的答案
- 如何通过服务器发送事件（SSE）实现流式传输，类似OpenAI的方式
- Panacea特定扩展（`anote_sources`，`anote_message_id`）在响应中出现的位置

## 这很重要的原因

大量现有工具——LangChain集成、内部脚本、第三方代理框架——都是针对OpenAI SDK的形状（`client.chat.completions.create(...)`，`client.models.list()`）编写的。Panacea提供了一个即插即用的客户端，使用相同的接口，这样团队就可以在不重写集成代码的情况下采用Panacea的私有文档基础后端，而不是要求每个集成者学习一个定制的Panacea SDK。

## 关键Panacea文件

| 文件 | 重要性 |
|---|---|
| `Panacea/backend/sdk/anoteai/openai_compat.py` | `AnoteOpenAI` 客户端：`CompletionsClient`，`ModelsClient`，`DocumentsClient`，以及SSE流解析器 |
| `Panacea/backend/sdk/anoteai/core.py` | 兼容层包装的底层 `PrivateChatbot` SDK 类 |
| `Panacea/backend/sdk/anoteai/handlers/private_handlers.py` | 与原生SDK共享的请求处理 |
| 服务器路由：`POST /v1/chat/completions`，`GET /v1/models`，`POST /v1/question-answer`，`POST /public/upload` | 客户端调用的OpenAI形状（以及一个Panacea特定）端点 |

## 工作原理

1. 像OpenAI SDK一样实例化客户端，但指向您的Panacea后端：

   ```python
   from anoteai.openai_compat import AnoteOpenAI

   client = AnoteOpenAI(
       api_key="your-anote-api-key",       # 或设置 ANOTE_API_KEY
       base_url="http://localhost:5000",    # 或 https://api.anote.ai
   )
   ```

2. 对于基于文档的问答，首先上传文件——`client.documents.upload(...)` 将多部分表单数据发布到 `/public/upload` 并返回 `chat_id`。
3. 以与调用OpenAI SDK相同的方式提问，通过 `extra_body` 传递 `chat_id` 以便服务器知道要检索哪些文档：

   ```python
   upload_resp = client.documents.upload("path/to/report.pdf")
   chat_id = upload_resp["chat_id"]

   response = client.chat.completions.create(
       model="gpt-4o",
       messages=[{"role": "user", "content": "总结关键发现。"}],
       extra_body={"chat_id": chat_id},
   )
   print(response.choices[0].message.content)
   print("来源:", response.anote_sources)
   ```

4. 响应被映射到与真实OpenAI SDK相对应的数据类（`ChatCompletion`，`Choice`，`Message`，`Usage`），加上两个Panacea扩展：`anote_message_id` 和 `anote_sources`（支持答案的检索块/引用）。
5. 传递 `stream=True` 以获取从 `text/event-stream` SSE 行解析的 `ChatCompletionChunk` 对象生成器（每个令牌的 `data: {...}`，以 `data: [DONE]` 结束）——与OpenAI的流式客户端生成的形状相同。
6. `client.models.list()` 调用 `GET /v1/models` 进行模型发现，返回与OpenAI SDK相同的 `Model`/`ModelList` 对象。

## 本地运行

从工作区根目录（`anote/panacea`）：

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

安装客户端的一个依赖并设置您的API密钥：

```bash
pip install requests
export ANOTE_API_KEY=your_api_key_here   # macOS/Linux
set ANOTE_API_KEY=your_api_key_here      # Windows cmd
```

### 最小化演练

```python
from anoteai.openai_compat import AnoteOpenAI

client = AnoteOpenAI(base_url="http://localhost:5000")

# 普通聊天，无文档：
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "法国的首都是什么？"}],
)
print(response.choices[0].message.content)

# 流式传输：
for chunk in client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "数到五。"}],
    stream=True,
):
    for choice in chunk.choices:
        if choice.delta.content:
            print(choice.delta.content, end="", flush=True)
```

## 食谱说明

本食谱是食谱03的良好补充——它具有相同的文档问答/RAG能力，但通过现有的基于OpenAI SDK的工具可以无修改地消费。值得提醒读者的是，`DocumentsClient.upload()`/`question_answer()` 是在OpenAI兼容核心之上分层的Panacea特定助手，而不是OpenAI规范本身的一部分。
