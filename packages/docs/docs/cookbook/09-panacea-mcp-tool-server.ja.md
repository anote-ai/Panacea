# Panacea MCPツールサーバー

このレシピでは、Panaceaがどのようにそのドキュメント/チャットのプリミティブを標準の[モデルコンテキストプロトコル](https://modelcontextprotocol.io/) (MCP)ツールとして公開するかを説明します。これにより、MCP互換のクライアント（Claude Desktop、他のMCPホスト）がPanaceaの検索およびチャット履歴機能を直接利用できるようになります。

## 学べること

- このMCPインターフェースとレシピ04の内部エージェント/ツール登録アーキテクチャの違い
- どのドキュメントおよびチャット操作がMCPツールとして公開されているか
- ドキュメントの取り込みがRayのリモートタスクを介してブロッキングしない理由
- 生のSQLパススルーツールが考慮すべきセキュリティ上の理由

## 重要な理由

レシピ04では、Panaceaの*内部*オーケストレーターがツールを登録して自分のエージェントが呼び出す方法を説明しています。これは異なる統合インターフェースです：同じ基盤となるドキュメント/チャット機能を**外部の標準化されたMCPツール**としてパッケージ化し、どのMCPクライアントでも呼び出せるようにします — Panacea特有のSDKやAPI契約は不要で、MCPプロトコルだけで済みます。

## 主要なPanaceaファイル

| ファイル | 重要な理由 |
|---|---|
| `Panacea/backend/mcp/mcp_server.py` | `FastMCP("Document Agent Server")` — すべての9つのMCPツールを定義 |
| `Panacea/backend/api_endpoints/financeGPT/chatbot_endpoints.py` | 各MCPツールがラップする基盤となるDB向け関数（`get_relevant_chunks`、`add_document_to_db`、`chunk_document`など） |
| `Panacea/backend/database/db.py` | `get_db_connection` — `execute_database_query`ツールによって直接使用される |

## 仕組み

1. `mcp_server.py`はRayを初期化し（`ray.init(...)`）、`"Document Agent Server"`という名前の`FastMCP`サーバーインスタンスを作成します。
2. `@mcp.tool()`で装飾された各関数は、既存のPanacea関数をラップし、プレーンテキストの結果またはエラーストリングを返します — LLMツール呼び出しが期待する形：
   - `retrieve_relevant_chunks(query, chat_id, user_email, k=2)` — `get_relevant_chunks`を介したチャットのドキュメントに対するセマンティック検索
   - `ingest_document(text, document_name, chat_id, chunk_size=1000)` — `add_document_to_db`を介してドキュメントを登録
   - `list_documents(chat_id, user_email)` / `delete_document(doc_id, user_email)` — ドキュメント管理
   - `add_message` / `get_chat_history` — チャット履歴の読み書き
   - `add_sources_to_message` — 保存されたメッセージに引用を添付
   - `extract_text_from_url(url)` — URLからテキストコンテンツを取得して返す
   - `execute_database_query(query, params)` — 生のSQLパススルー（以下のセキュリティノートを参照）
3. `ingest_document`はチャンク化でブロックしません — `chunk_document.remote(text, chunk_size, doc_id)`というRayのリモートタスクを呼び出すため、大きなドキュメントは非同期に処理され、ツール呼び出しは即座に戻ります。
4. `python backend/mcp/mcp_server.py`を実行すると、`mcp.run()`が開始され、これらのツールがMCPのstdioトランスポートを介して提供されます — MCPクライアントが起動して接続できる準備が整います。
5. このスクリプトを起動するように設定されたMCPクライアント（例：Claude Desktop）は、Panacea特有の統合コードを書くことなく、すべての9つのツールに自動的にアクセスできます。

### セキュリティノート

`execute_database_query`は、許可リストや読み取り専用制限なしに本番接続に対して任意のSQL文字列を実行します — `SELECT`クエリは行をJSONとして返し、それ以外はコミットされて影響を受けた行数を返します。これは最小特権の領域として扱ってください：信頼できないMCPクライアントにこのサーバーを公開する場合は、このツールを削除するか、DBユーザーのスコープを非機密テーブルに対する読み取り専用アクセスに制限してください。

## ローカルで実行する

ワークスペースのルート（`anote/panacea`）から：

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build   # MySQL、Redis、Tika、およびバックエンドを起動
```

MCPサーバーには`fastmcp`が必要です（現在`backend/requirements.txt`に固定されていないため、別途インストールしてください）および`ray>=2.9.0`（すでに`backend/requirements.txt`に含まれています）：

```bash
pip install fastmcp
cd Panacea/backend
python mcp/mcp_server.py
```

### MCPクライアントを接続する

MCP互換のクライアントをスクリプトにポイントします。例えば、Claude Desktopの`claude_desktop_config.json`で：

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

クライアントを再起動すると、上記の9つのツールがチャットから呼び出せるようになります。

## クックブックのためのノート

レシピ04の良いフォローアップです — 内部ツール登録（オーケストレーター内の`register_tool()`）とこの外部MCPインターフェースを対比させます。また、読者にとってのギャップとして注目すべき点：`fastmcp`はまだ`backend/requirements.txt`にリストされていないため、これが上流で修正されるまで手動でインストールする必要があります。
