# Servidor da Ferramenta MCP do Panacea

Esta receita explica como o Panacea expõe seus primitivos de documento/chat como ferramentas padrão do [Modelo de Protocolo de Contexto](https://modelcontextprotocol.io/) (MCP), para que qualquer cliente compatível com MCP (Claude Desktop, outros hosts MCP) possa usar diretamente as capacidades de recuperação e histórico de chat do Panacea.

## O que você vai aprender

- A diferença entre esta superfície MCP e a arquitetura interna de registro de agentes/ferramentas da receita 04
- Quais operações de documento e chat são expostas como ferramentas MCP
- Como a ingestão de documentos permanece não bloqueante por meio de uma tarefa remota Ray
- Por que a ferramenta de passagem de SQL bruto é uma consideração de segurança que vale a pena destacar

## Por que isso é importante

A receita 04 cobre como o orquestrador *interno* do Panacea registra ferramentas para que seus próprios agentes chamem. Esta é uma superfície de integração diferente: ela empacota as mesmas funções subjacentes de documento/chat como **ferramentas MCP externas e padronizadas** que qualquer cliente MCP pode invocar — nenhum SDK ou contrato de API específico do Panacea é necessário, apenas o protocolo MCP.

## Principais arquivos do Panacea

| Arquivo | Por que é importante |
|---|---|
| `Panacea/backend/mcp/mcp_server.py` | `FastMCP("Servidor do Agente de Documentos")` — define todas as nove ferramentas MCP |
| `Panacea/backend/api_endpoints/financeGPT/chatbot_endpoints.py` | As funções subjacentes que cada ferramenta MCP envolve (`get_relevant_chunks`, `add_document_to_db`, `chunk_document`, etc.) |
| `Panacea/backend/database/db.py` | `get_db_connection` — usado diretamente pela ferramenta `execute_database_query` |

## Como funciona

1. `mcp_server.py` inicializa o Ray (`ray.init(...)`) e uma instância do servidor `FastMCP` chamada `"Servidor do Agente de Documentos"`.
2. Cada função decorada com `@mcp.tool()` envolve uma função existente do Panacea e retorna um resultado em texto simples ou uma string de erro — o formato que uma chamada de ferramenta LLM espera de volta:
   - `retrieve_relevant_chunks(query, chat_id, user_email, k=2)` — busca semântica sobre os documentos de um chat via `get_relevant_chunks`
   - `ingest_document(text, document_name, chat_id, chunk_size=1000)` — registra um documento via `add_document_to_db`
   - `list_documents(chat_id, user_email)` / `delete_document(doc_id, user_email)` — gerenciamento de documentos
   - `add_message` / `get_chat_history` — leitura/escrita do histórico de chat
   - `add_sources_to_message` — anexar citações a uma mensagem armazenada
   - `extract_text_from_url(url)` — buscar e retornar o conteúdo de texto de uma URL
   - `execute_database_query(query, params)` — passagem de SQL bruto (veja a nota de segurança abaixo)
3. `ingest_document` não bloqueia na fragmentação — chama `chunk_document.remote(text, chunk_size, doc_id)`, uma tarefa remota Ray, assim documentos grandes são processados de forma assíncrona enquanto a chamada da ferramenta retorna imediatamente.
4. Executar `python backend/mcp/mcp_server.py` inicia `mcp.run()`, que serve essas ferramentas através do transporte stdio do MCP — pronto para um cliente MCP ser iniciado e conectado.
5. Um cliente MCP (por exemplo, Claude Desktop) configurado para iniciar este script tem acesso a todas as nove ferramentas automaticamente, sem precisar escrever nenhum código de integração específico do Panacea.

### Nota de segurança

`execute_database_query` executa uma string SQL arbitrária contra a conexão de produção sem lista de permissão ou restrição de somente leitura — consultas `SELECT` retornam linhas como JSON, qualquer outra coisa comita e retorna a contagem de linhas afetadas. Trate isso como território de menor privilégio: se você expuser este servidor a um cliente MCP que não confia totalmente, remova esta ferramenta ou limite seu usuário de DB a acesso somente leitura em tabelas não sensíveis.

## Execute localmente

A partir da raiz do workspace (`anote/panacea`):

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build   # inicia MySQL, Redis, Tika e o backend
```

O servidor MCP precisa de `fastmcp` (não está atualmente listado em `backend/requirements.txt` — instale separadamente) e `ray>=2.9.0` (já está em `backend/requirements.txt`):

```bash
pip install fastmcp
cd Panacea/backend
python mcp/mcp_server.py
```

### Conectar um cliente MCP

Aponte um cliente compatível com MCP para o script, por exemplo, no `claude_desktop_config.json` do Claude Desktop:

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

Reinicie o cliente, e as nove ferramentas acima estarão disponíveis para invocar a partir do chat.

## Notas para o livro de receitas

Bom acompanhamento da receita 04 — contraste o registro de ferramentas internas (`register_tool()` dentro do orquestrador) com esta superfície MCP externa. Também vale a pena notar como uma lacuna para os leitores: `fastmcp` ainda não está listado em `backend/requirements.txt`, então precisa de uma instalação manual até que isso seja corrigido upstream.
