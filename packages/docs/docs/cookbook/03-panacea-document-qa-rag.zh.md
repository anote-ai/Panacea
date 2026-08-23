# Panacea 文档问答 + RAG

本食谱解释了 Panacea 如何构建私有文档问答与检索增强生成 (RAG)。

## 您将学到什么

- Panacea 如何摄取文档并将其存储为可搜索的文本
- 后端如何检索与问题相关的片段
- 系统如何使用嵌入和文档来源来支撑答案
- 如何捕获问答反馈并改善未来的响应

## 这为什么重要

Panacea 旨在让团队可以询问私有文档而无需将其发送到第三方聊天服务。工作流程如下：

1. 上传文档
2. 切分并嵌入内容
3. 为用户查询检索相关片段
4. 使用带引用的 LLM 回答
5. 捕获反馈以提高质量

## 关键的 Panacea 文件

| 文件 | 重要性 |
|---|---|
| `Panacea/backend/api_endpoints/documents/handler.py` | 文档上传和摄取 API 路由 |
| `Panacea/backend/database/db.py` | 文档存储和检索 SQL 逻辑 |
| `Panacea/backend/database/qa_feedback.py` | 文档问答的反馈捕获 |
| `Panacea/backend/agents/multi_agent_system.py` | 在多代理工作流中使用的文档检索代理 |

## 它是如何工作的

- 文档通过后端上传并存储在 `documents.document_text` 中。
- 系统切分大型文档并创建检索元数据以便快速查找。
- 当用户提出问题时，Panacea 选择一个或多个专门的代理来检索最佳片段，然后生成答案。
- 结果包括来源引用，以便用户可以追溯答案到原始文档。
- 反馈信号记录在 `qa_feedback` 中，以便未来进行质量改进。

## 本地运行

从工作区根目录 (`anote/panacea`) 开始：

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

这将启动后端、Web 应用、MySQL、Redis 和 Tika。

如果您已经在食谱文件夹中，请使用：

```bash
cd ../../../Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

打开 `http://localhost:3000` 使用 Panacea Web UI。文档上传通过后端路由 `POST /ingest-pdf` 处理，所需的表单字段为 `chat_id` 和 `files[]`。

示例上传命令：

```bash
curl -X POST http://localhost:5000/ingest-pdf \
  -F chat_id=1 \
  -F "files[]=@./path/to/document.pdf"
```

### 最小上传操作指南

1. 从代码库根目录启动 Panacea：

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

2. 在另一个终端中，上传单个文本或 PDF 文档：

```bash
curl -X POST http://localhost:5000/ingest-pdf \
  -F chat_id=1 \
  -F "files[]=@./Cookbook/recipes/03-panacea-document-qa-rag/data/sample-doc.txt"
```

3. 确认后端返回成功的 `Document Uploaded` 响应。

4. 使用 `http://localhost:3000` 的 Web UI，选择相同的聊天会话以询问有关上传文档的问题。

如果您想在上传后直接测试 API，请在 UI 或数据库中找到聊天会话 ID，并通过应用的聊天流程发送问题。Panacea 将检索相关片段并生成支撑答案。

## 食谱注意事项

本食谱非常适合解释 Panacea 如何支持私有知识工作的食谱条目。它比一行脚本更具概念性，因为真正的价值在于理解文档摄取和检索架构。
