# Panacea 文件問答 + RAG

本食譜解釋了 Panacea 如何使用檢索增強生成 (RAG) 建立私有文件的問答系統。

## 您將學到什麼

- Panacea 如何攝取文件並將其儲存為可搜尋的文本
- 後端如何檢索與問題相關的片段
- 系統如何使用嵌入和文件來源來支持答案
- 如何捕捉問答反饋並改善未來的回應

## 為什麼這很重要

Panacea 的設計旨在讓團隊可以對私有文件提出問題，而無需將其發送到第三方聊天服務。工作流程如下：

1. 上傳文件
2. 切割並嵌入內容
3. 為用戶查詢檢索相關片段
4. 使用 LLM 進行回答並附上引用
5. 捕捉反饋以提高質量

## 主要的 Panacea 文件

| 文件 | 重要性 |
|---|---|
| `Panacea/backend/api_endpoints/documents/handler.py` | 文件上傳和攝取的 API 路由 |
| `Panacea/backend/database/db.py` | 文件儲存和檢索的 SQL 邏輯 |
| `Panacea/backend/database/qa_feedback.py` | 文件問答的反饋捕捉 |
| `Panacea/backend/agents/multi_agent_system.py` | 用於多代理工作流程的文件檢索代理 |

## 它是如何運作的

- 文件通過後端上傳並儲存在 `documents.document_text` 中。
- 系統將大型文件切割並創建檢索元數據以便快速查找。
- 當用戶提出問題時，Panacea 選擇一個或多個專門的代理來檢索最佳片段，然後生成答案。
- 結果包括來源引用，以便用戶可以追溯答案到原始文件。
- 反饋信號被記錄在 `qa_feedback` 中，以便未來的質量改進。

## 本地運行

從工作區根目錄 (`anote/panacea`)：

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

這將啟動後端、網頁應用程式、MySQL、Redis 和 Tika。

如果您已經在食譜文件夾內，請使用：

```bash
cd ../../../Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

打開 `http://localhost:3000` 使用 Panacea 網頁 UI。文件上傳由後端路由 `POST /ingest-pdf` 處理，所需的表單字段為 `chat_id` 和 `files[]`。

示例上傳命令：

```bash
curl -X POST http://localhost:5000/ingest-pdf \
  -F chat_id=1 \
  -F "files[]=@./path/to/document.pdf"
```

### 最小上傳操作指南

1. 從倉庫根目錄啟動 Panacea：

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

2. 在另一個終端中，上傳單個文本或 PDF 文件：

```bash
curl -X POST http://localhost:5000/ingest-pdf \
  -F chat_id=1 \
  -F "files[]=@./Cookbook/recipes/03-panacea-document-qa-rag/data/sample-doc.txt"
```

3. 確認後端返回成功的 `Document Uploaded` 回應。

4. 使用 `http://localhost:3000` 的網頁 UI，並選擇相同的聊天會話以詢問有關上傳文件的問題。

如果您想在上傳後直接測試 API，請在 UI 或數據庫中找到聊天會話 ID，並通過應用程式的聊天流程發送問題。Panacea 將檢索相關片段並生成有根據的答案。

## 食譜的注意事項

本食譜非常適合用於解釋 Panacea 如何支持私有知識工作的食譜條目。它比單行腳本更具概念性，因為真正的價值在於理解文件攝取和檢索架構。
