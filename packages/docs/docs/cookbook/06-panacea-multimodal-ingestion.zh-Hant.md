# Panacea 多模態文件攝取

本食譜解釋了 Panacea 如何將文件問答 + RAG（參見 [食譜 03](03-panacea-document-qa-rag.md)）擴展到圖像、音頻、視頻和電子表格——使所有這些都可以通過相同的分塊和嵌入管道進行搜索。

## 您將學到什麼

- Panacea 如何根據 MIME 類型對上傳進行分類並將其路由到專用的攝取服務
- 圖像和視頻幀如何使用具備視覺能力的 LLM 轉換為可索引的文本
- 音頻（包括視頻的音軌）如何使用 Whisper 進行轉錄
- 電子表格如何轉換為 Markdown 表格，而不是被壓平為不可搜索的文本轉儲
- 管控多模態攝取的功能標誌和大小限制

## 為什麼這很重要

Tika（默認的文件文本提取器）只能有效處理基於文本的格式。如果沒有額外處理，上傳的圖像、音頻片段、視頻或電子表格將無法攝取或失去所有結構。相反，Panacea 在上傳時檢測媒體類型並調用一個專門構建的服務，該服務生成乾淨的文本，然後將其存儲為 `document_text`，並通過與其他文件完全相同的檢索路徑流動——因此，截圖、通話錄音或銷售電子表格都可以像 PDF 一樣通過聊天進行回答。

## 主要的 Panacea 文件

| 文件 | 重要性 |
|---|---|
| `Panacea/backend/api_endpoints/documents/handler.py` | 在上傳時檢測 MIME 類型/擴展名並路由到正確的攝取服務 |
| `Panacea/backend/services/vision_service.py` | `describe_image()` — 使用 GPT-4o 或 Claude 視覺生成圖像的詳細文本描述 |
| `Panacea/backend/services/audio_service.py` | `transcribe_audio()` — 使用 OpenAI Whisper 轉錄音頻 |
| `Panacea/backend/services/video_service.py` | 使用 `ffmpeg` 提取幀，並使用視覺服務描述每個幀，單獨轉錄音軌，並將兩者交錯在一起 |
| `Panacea/backend/services/tabular_service.py` | `ingest_tabular()` — 將 CSV/TSV/XLSX/XLS/ODS 轉換為保留標題和行的 Markdown 表格 |
| `Panacea/backend/agents/config.py` | `AgentConfig` 功能標誌：`ENABLE_MULTIMODAL`、`MAX_IMAGE_BYTES`、`MAX_AUDIO_BYTES`、`MAX_VIDEO_BYTES`、`VIDEO_FRAME_INTERVAL_SECS`、`VIDEO_MAX_FRAMES` |

## 它是如何工作的

1. 通過用於常規文件的相同端點上傳文件；`handler.py` 嗅探 MIME 類型/擴展名以將其分類為圖像、視頻、音頻、表格或純文本/文件。
2. **圖像** → `vision_service.describe_image()` 將圖像（base64 編碼）發送到具備視覺能力的模型，並指示其轉錄任何可見文本、描述圖表/圖示/UI 截圖，並注意物體和佈局——因此僅描述就足以讓語義搜索稍後找到它。
3. **音頻** → `audio_service.transcribe_audio()` 調用 Whisper（`whisper-1`）並返回帶有持續時間/語言元數據的轉錄文本。
4. **視頻** → `video_service` 在固定間隔（`VIDEO_FRAME_INTERVAL_SECS`，默認 30 秒，限制為 `VIDEO_MAX_FRAMES`）使用 `ffmpeg` 提取幀，使用視覺服務描述每個幀，單獨轉錄音軌，並將兩者交錯在一起形成一個帶時間戳的文件。
5. **表格** → `tabular_service.ingest_tabular()` 原生解析每個工作表（通過 `csv`/`pandas`+`openpyxl`/`xlrd`）並將其呈現為 Markdown 表格，對於超過前 500 行的行回退到普通 CSV，以便即使未漂亮呈現也不會從搜索索引中丟失任何內容。
6. 從這些服務中產生的任何文本都存儲為 `document_text`，並像普通文件一樣進行分塊/嵌入，因此可以通過標準 RAG 問答流程從食譜 03 中檢索。

每個服務都設計為**永不引發錯誤**——失敗的視覺調用、缺失的依賴項或超大文件都會返回佔位符字符串（例如 `"[圖像過大，無法進行內聯分析（23.4 MB）。限制：20 MB。]"`），因此文件記錄始終會創建，而不會導致整個上傳失敗。

## 本地運行

從工作區根目錄（`anote/panacea`）：

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

多模態攝取默認為開啟（`ENABLE_MULTIMODAL=true`）。在 `backend/.env` 中設置以下參數以調整行為：

```bash
ENABLE_MULTIMODAL=true        # 主開關
MAX_IMAGE_BYTES=20971520      # 默認 20 MB
MAX_AUDIO_BYTES=26214400      # 默認 25 MB
MAX_VIDEO_BYTES=524288000     # 默認 500 MB
VIDEO_FRAME_INTERVAL_SECS=30
VIDEO_MAX_FRAMES=20
```

視頻攝取還需要在後端容器的 `PATH` 中存在 `ffmpeg`（已包含在提供的 Docker 映像中）。Excel 攝取需要 `openpyxl`（XLSX/ODS）和 `xlrd`（舊版 XLS），而且兩個視覺/音頻服務需要根據 `DEFAULT_AGENT_MODEL_TYPE` 設置 `OPENAI_API_KEY` 和/或 `ANTHROPIC_API_KEY`。

### 嘗試一下

```bash
curl -X POST http://localhost:5000/ingest-pdf \
  -F chat_id=1 \
  -F "files[]=@./screenshot.png"

curl -X POST http://localhost:5000/ingest-pdf \
  -F chat_id=1 \
  -F "files[]=@./quarterly_sales.xlsx"
```

然後，在 `http://localhost:3000` 的網頁 UI 中，打開相同的聊天會話並詢問有關您剛上傳的圖像或電子表格的問題——Panacea 將根據生成的描述/Markdown 表格回答，正如它從 PDF 中所做的一樣。

## 食譜的注意事項

本食譜與食譜 03 配對良好：它是相同的 RAG 管道，只是輸入格式的範圍更廣。值得提醒讀者的是，圖像/視頻的“索引質量”僅取決於視覺模型的描述，因此在 `vision_service.py` 的 `_INDEXING_PROMPT` 中進行提示調整是一個自然的自定義點。
