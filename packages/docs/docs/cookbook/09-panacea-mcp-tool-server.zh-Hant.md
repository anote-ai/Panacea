# Panacea MCP 工具伺服器

本食譜解釋了 Panacea 如何將其文件/聊天原語公開為標準 [模型上下文協議](https://modelcontextprotocol.io/) (MCP) 工具，因此任何兼容 MCP 的客戶端（Claude Desktop、其他 MCP 主機）都可以直接使用 Panacea 的檢索和聊天歷史功能。

## 您將學到什麼

- 此 MCP 表面與食譜 04 中的內部代理/工具註冊架構之間的區別
- 哪些文件和聊天操作被公開為 MCP 工具
- 文件攝取如何通過 Ray 遠程任務保持非阻塞
- 為什麼原始 SQL 透傳工具是一個值得注意的安全考量

## 為什麼這很重要

食譜 04 涵蓋了 Panacea 的 *內部* 協調器如何為其自己的代理註冊工具。這是一個不同的整合表面：它將相同的底層文件/聊天功能打包為 **外部、標準化的 MCP 工具**，任何 MCP 客戶端都可以調用 — 無需特定於 Panacea 的 SDK 或 API 合約，只需 MCP 協議。

## 主要 Panacea 檔案

| 檔案 | 重要性 |
|---|---|
| `Panacea/backend/mcp/mcp_server.py` | `FastMCP("Document Agent Server")` — 定義所有九個 MCP 工具 |
| `Panacea/backend/api_endpoints/financeGPT/chatbot_endpoints.py` | 每個 MCP 工具包裝的底層 DB 面向函數 (`get_relevant_chunks`, `add_document_to_db`, `chunk_document`, 等) |
| `Panacea/backend/database/db.py` | `get_db_connection` — 被 `execute_database_query` 工具直接使用 |

## 它是如何運作的

1. `mcp_server.py` 初始化 Ray (`ray.init(...)`) 和一個名為 `"Document Agent Server"` 的 `FastMCP` 伺服器實例。
2. 每個用 `@mcp.tool()` 裝飾的函數包裝一個現有的 Panacea 函數，並返回一個純文本結果或錯誤字符串 — LLM 工具調用期望的形狀：
   - `retrieve_relevant_chunks(query, chat_id, user_email, k=2)` — 通過 `get_relevant_chunks` 對聊天的文件進行語義搜索
   - `ingest_document(text, document_name, chat_id, chunk_size=1000)` — 通過 `add_document_to_db` 註冊一個文件
   - `list_documents(chat_id, user_email)` / `delete_document(doc_id, user_email)` — 文件管理
   - `add_message` / `get_chat_history` — 聊天歷史的讀取/寫入
   - `add_sources_to_message` — 將引用附加到存儲的消息
   - `extract_text_from_url(url)` — 從 URL 獲取並返回文本內容
   - `execute_database_query(query, params)` — 原始 SQL 透傳（見下方安全說明）
3. `ingest_document` 不會在分塊上阻塞 — 它調用 `chunk_document.remote(text, chunk_size, doc_id)`，這是一個 Ray 遠程任務，因此大型文件會異步處理，而工具調用會立即返回。
4. 執行 `python backend/mcp/mcp_server.py` 啟動 `mcp.run()`，該命令通過 MCP 的 stdio 傳輸提供這些工具 — 準備好讓 MCP 客戶端啟動並連接。
5. 配置為啟動此腳本的 MCP 客戶端（例如 Claude Desktop）將自動獲得所有九個工具的訪問權限，而無需編寫任何特定於 Panacea 的整合代碼。

### 安全說明

`execute_database_query` 對生產連接執行任意 SQL 字符串，沒有允許列表或只讀限制 — `SELECT` 查詢返回 JSON 格式的行，其他任何操作都會提交並返回受影響的行數。將此視為最小特權範疇：如果您將此伺服器暴露給不完全信任的 MCP 客戶端，則應刪除此工具或將其 DB 用戶範圍限制為對非敏感表的只讀訪問。

## 本地運行

從工作區根目錄 (`anote/panacea`)：

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build   # 啟動 MySQL、Redis、Tika 和後端
```

MCP 伺服器需要 `fastmcp`（目前未在 `backend/requirements.txt` 中固定 — 需單獨安裝）和 `ray>=2.9.0`（已在 `backend/requirements.txt` 中）：

```bash
pip install fastmcp
cd Panacea/backend
python mcp/mcp_server.py
```

### 連接 MCP 客戶端

將兼容 MCP 的客戶端指向該腳本，例如在 Claude Desktop 的 `claude_desktop_config.json` 中：

```json
{
  "mcpServers": {
    "panacea-documents": {
      "command": "python",
      "args": ["/absolute/path/to/Panacea/backend/mcp/mcp_server.py"]
    }
  }
}
```

重新啟動客戶端，以上九個工具將可用於從聊天中調用。

## 食譜的注意事項

是食譜 04 的良好後續 — 將內部工具註冊（協調器內的 `register_tool()`）與此外部 MCP 表面進行對比。還值得注意的是，對於讀者來說：`fastmcp` 尚未列在 `backend/requirements.txt` 中，因此在上游修復之前需要手動安裝。
