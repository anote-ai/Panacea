# Panacea MCP 工具服务器

本食谱解释了 Panacea 如何将其文档/聊天原语暴露为标准 [模型上下文协议](https://modelcontextprotocol.io/) (MCP) 工具，以便任何兼容 MCP 的客户端（Claude Desktop、其他 MCP 主机）可以直接使用 Panacea 的检索和聊天历史功能。

## 你将学到什么

- 这个 MCP 接口与食谱 04 中的内部代理/工具注册架构之间的区别
- 哪些文档和聊天操作被暴露为 MCP 工具
- 文档摄取如何通过 Ray 远程任务保持非阻塞
- 原始 SQL 透传工具为何是一个值得关注的安全考虑

## 这为什么重要

食谱 04 涉及 Panacea 的 *内部* 调度器如何为其自己的代理注册工具。这是一个不同的集成接口：它将相同的底层文档/聊天功能打包为 **外部、标准化的 MCP 工具**，任何 MCP 客户端都可以调用——不需要特定于 Panacea 的 SDK 或 API 合同，仅需 MCP 协议。

## 关键的 Panacea 文件

| 文件 | 重要性 |
|---|---|
| `Panacea/backend/mcp/mcp_server.py` | `FastMCP("Document Agent Server")` — 定义所有九个 MCP 工具 |
| `Panacea/backend/api_endpoints/financeGPT/chatbot_endpoints.py` | 每个 MCP 工具包装的底层数据库功能 (`get_relevant_chunks`, `add_document_to_db`, `chunk_document`, 等) |
| `Panacea/backend/database/db.py` | `get_db_connection` — 被 `execute_database_query` 工具直接使用 |

## 它是如何工作的

1. `mcp_server.py` 初始化 Ray (`ray.init(...)`) 和一个名为 `"Document Agent Server"` 的 `FastMCP` 服务器实例。
2. 每个用 `@mcp.tool()` 装饰的函数包装一个现有的 Panacea 函数，并返回一个纯文本结果或错误字符串——这是 LLM 工具调用期望的形状：
   - `retrieve_relevant_chunks(query, chat_id, user_email, k=2)` — 通过 `get_relevant_chunks` 对聊天的文档进行语义搜索
   - `ingest_document(text, document_name, chat_id, chunk_size=1000)` — 通过 `add_document_to_db` 注册文档
   - `list_documents(chat_id, user_email)` / `delete_document(doc_id, user_email)` — 文档管理
   - `add_message` / `get_chat_history` — 聊天历史的读/写
   - `add_sources_to_message` — 将引用附加到存储的消息
   - `extract_text_from_url(url)` — 从 URL 获取并返回文本内容
   - `execute_database_query(query, params)` — 原始 SQL 透传（见下面的安全说明）
3. `ingest_document` 在分块时不会阻塞——它调用 `chunk_document.remote(text, chunk_size, doc_id)`，这是一个 Ray 远程任务，因此大型文档会异步处理，而工具调用会立即返回。
4. 运行 `python backend/mcp/mcp_server.py` 启动 `mcp.run()`，通过 MCP 的 stdio 传输提供这些工具——准备好让 MCP 客户端启动并连接。
5. 配置为启动此脚本的 MCP 客户端（例如 Claude Desktop）将自动获得对所有九个工具的访问权限，无需编写任何特定于 Panacea 的集成代码。

### 安全说明

`execute_database_query` 在生产连接上执行任意 SQL 字符串，没有允许列表或只读限制——`SELECT` 查询返回 JSON 格式的行，其他任何操作都会提交并返回受影响的行数。将此视为最小权限区域：如果您将此服务器暴露给不完全信任的 MCP 客户端，请删除此工具或将其数据库用户的权限限制为对非敏感表的只读访问。

## 本地运行

从工作区根目录 (`anote/panacea`)：

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build   # 启动 MySQL、Redis、Tika 和后端
```

MCP 服务器需要 `fastmcp`（目前未在 `backend/requirements.txt` 中固定——请单独安装）和 `ray>=2.9.0`（已在 `backend/requirements.txt` 中）：

```bash
pip install fastmcp
cd Panacea/backend
python mcp/mcp_server.py
```

### 连接 MCP 客户端

将兼容 MCP 的客户端指向该脚本，例如在 Claude Desktop 的 `claude_desktop_config.json` 中：

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

重启客户端，上述九个工具将可用于从聊天中调用。

## 食谱的注意事项

作为食谱 04 的良好后续——对比内部工具注册（调度器内部的 `register_tool()`）与此外部 MCP 接口。还值得注意的是，`fastmcp` 目前尚未列在 `backend/requirements.txt` 中，因此在修复之前需要手动安装。
