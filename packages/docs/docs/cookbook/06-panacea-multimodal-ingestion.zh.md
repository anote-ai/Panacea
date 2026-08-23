# Panacea 多模态文档摄取

本食谱解释了 Panacea 如何将文档问答 + RAG（参见 [食谱 03](03-panacea-document-qa-rag.md)）扩展到图像、音频、视频和电子表格——使它们都可以通过相同的分块和嵌入管道进行搜索。

## 您将学习到的内容

- Panacea 如何通过 MIME 类型对上传进行分类，并将其路由到专用的摄取服务
- 图像和视频帧如何使用具有视觉能力的 LLM 转换为可索引的文本
- 音频（包括视频的音轨）如何使用 Whisper 进行转录
- 电子表格如何转换为 Markdown 表格，而不是被压缩成不可搜索的文本转储
- 管理多模态摄取的功能标志和大小限制

## 为什么这很重要

Tika（默认的文档文本提取器）只能有效处理基于文本的格式。如果没有额外处理，上传的图像、音频片段、视频或电子表格将无法摄取或失去所有结构。相反，Panacea 在上传时检测媒体类型，并调用一个专门构建的服务，生成干净的文本，然后将其存储为 `document_text`，并通过与任何其他文档完全相同的检索路径流动——因此，屏幕截图、通话录音或销售电子表格都可以像 PDF 一样通过聊天进行回答。

## 关键的 Panacea 文件

| 文件 | 重要性 |
|---|---|
| `Panacea/backend/api_endpoints/documents/handler.py` | 在上传时检测 MIME 类型/扩展名并路由到正确的摄取服务 |
| `Panacea/backend/services/vision_service.py` | `describe_image()` — 使用 GPT-4o 或 Claude 视觉生成图像的详细文本描述 |
| `Panacea/backend/services/audio_service.py` | `transcribe_audio()` — 使用 OpenAI Whisper 转录音频 |
| `Panacea/backend/services/video_service.py` | 使用 `ffmpeg` 提取帧，使用视觉服务描述每一帧，单独转录音轨，并将两者交错在一起 |
| `Panacea/backend/services/tabular_service.py` | `ingest_tabular()` — 将 CSV/TSV/XLSX/XLS/ODS 转换为保留标题和行的 Markdown 表格 |
| `Panacea/backend/agents/config.py` | `AgentConfig` 功能标志：`ENABLE_MULTIMODAL`，`MAX_IMAGE_BYTES`，`MAX_AUDIO_BYTES`，`MAX_VIDEO_BYTES`，`VIDEO_FRAME_INTERVAL_SECS`，`VIDEO_MAX_FRAMES` |

## 工作原理

1. 通过与常规文档相同的端点上传文件；`handler.py` 检测 MIME 类型/扩展名，将其分类为图像、视频、音频、表格或纯文本/文档。
2. **图像** → `vision_service.describe_image()` 将图像（base64 编码）发送到具有视觉能力的模型，并指示其转录任何可见文本，描述图表/图示/UI 截图，并注意对象和布局——因此，仅描述就足以让语义搜索在后续找到它。
3. **音频** → `audio_service.transcribe_audio()` 调用 Whisper（`whisper-1`）并返回带有持续时间/语言元数据的转录文本。
4. **视频** → `video_service` 以固定间隔（`VIDEO_FRAME_INTERVAL_SECS`，默认 30 秒，最大限制为 `VIDEO_MAX_FRAMES`）使用 `ffmpeg` 提取帧，使用视觉服务描述每一帧，单独转录音轨，并将两者交错成一个带时间戳的文档。
5. **表格** → `tabular_service.ingest_tabular()` 原生解析每个工作表（通过 `csv`/`pandas`+`openpyxl`/`xlrd`），并将其呈现为 Markdown 表格，对于超过前 500 行的行回退到普通 CSV，以确保即使未很好呈现也不会丢失搜索索引中的内容。
6. 从任何这些服务输出的文本都存储为 `document_text`，并像普通文档一样进行分块/嵌入，因此可以通过标准的 RAG 问答流程从食谱 03 中检索。

每个服务都设计为**绝不抛出异常**——失败的视觉调用、缺失的依赖项或超大的文件返回占位符字符串（例如 `"[图像过大，无法进行内联分析（23.4 MB）。限制：20 MB。]"`），因此文档记录始终会创建，而不会导致整个上传失败。

## 本地运行

从工作区根目录（`anote/panacea`）：

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

多模态摄取默认开启（`ENABLE_MULTIMODAL=true`）。在 `backend/.env` 中设置这些以调整行为：

```bash
ENABLE_MULTIMODAL=true        # 主开关
MAX_IMAGE_BYTES=20971520      # 默认 20 MB
MAX_AUDIO_BYTES=26214400      # 默认 25 MB
MAX_VIDEO_BYTES=524288000     # 默认 500 MB
VIDEO_FRAME_INTERVAL_SECS=30
VIDEO_MAX_FRAMES=20
```

视频摄取还需要在后端容器的 `PATH` 中存在 `ffmpeg`（已包含在提供的 Docker 镜像中）。Excel 摄取需要 `openpyxl`（XLSX/ODS）和 `xlrd`（旧版 XLS），并且两个视觉/音频服务需要根据 `DEFAULT_AGENT_MODEL_TYPE` 设置 `OPENAI_API_KEY` 和/或 `ANTHROPIC_API_KEY`。

### 尝试一下

```bash
curl -X POST http://localhost:5000/ingest-pdf \
  -F chat_id=1 \
  -F "files[]=@./screenshot.png"

curl -X POST http://localhost:5000/ingest-pdf \
  -F chat_id=1 \
  -F "files[]=@./quarterly_sales.xlsx"
```

然后，在 `http://localhost:3000` 的网页 UI 中，打开相同的聊天会话，并询问有关您刚上传的图像或电子表格的问题——Panacea 根据生成的描述/Markdown 表格进行回答，正如它从 PDF 中那样。

## 食谱的注意事项

本食谱与食谱 03 配对良好：它是相同的 RAG 管道，只是输入格式的漏斗更宽。值得提醒读者的是，图像/视频的“索引质量”仅与视觉模型的描述一样好，因此在 `vision_service.py` 的 `_INDEXING_PROMPT` 中进行提示调优是一个自然的自定义点。
