# Servidor de Herramientas MCP de Panacea

Esta receta explica cómo Panacea expone sus primitivas de documento/chat como herramientas estándar del [Protocolo de Contexto de Modelo](https://modelcontextprotocol.io/) (MCP), de modo que cualquier cliente compatible con MCP (Claude Desktop, otros anfitriones MCP) pueda utilizar las capacidades de recuperación y el historial de chat de Panacea directamente.

## Lo que aprenderás

- La diferencia entre esta superficie MCP y la arquitectura interna de registro de agentes/herramientas de la receta 04
- Qué operaciones de documento y chat se exponen como herramientas MCP
- Cómo la ingestión de documentos permanece no bloqueante a través de una tarea remota de Ray
- Por qué la herramienta de paso de SQL en bruto es una consideración de seguridad que vale la pena mencionar

## Por qué esto es importante

La receta 04 cubre cómo el *orquestador* interno de Panacea registra herramientas para que sus propios agentes las llamen. Esta es una superficie de integración diferente: empaqueta las mismas funciones subyacentes de documento/chat como **herramientas MCP externas y estandarizadas** que cualquier cliente MCP puede invocar — no se requiere un SDK o contrato API específico de Panacea, solo el protocolo MCP.

## Archivos clave de Panacea

| Archivo | Por qué es importante |
|---|---|
| `Panacea/backend/mcp/mcp_server.py` | `FastMCP("Servidor de Agente de Documentos")` — define todas las nueve herramientas MCP |
| `Panacea/backend/api_endpoints/financeGPT/chatbot_endpoints.py` | Las funciones subyacentes que cada herramienta MCP envuelve (`get_relevant_chunks`, `add_document_to_db`, `chunk_document`, etc.) |
| `Panacea/backend/database/db.py` | `get_db_connection` — utilizado directamente por la herramienta `execute_database_query` |

## Cómo funciona

1. `mcp_server.py` inicializa Ray (`ray.init(...)`) y una instancia del servidor `FastMCP` llamada `"Servidor de Agente de Documentos"`.
2. Cada función decorada con `@mcp.tool()` envuelve una función existente de Panacea y devuelve un resultado en texto plano o una cadena de error — la forma que espera una llamada de herramienta LLM:
   - `retrieve_relevant_chunks(query, chat_id, user_email, k=2)` — búsqueda semántica sobre los documentos de un chat a través de `get_relevant_chunks`
   - `ingest_document(text, document_name, chat_id, chunk_size=1000)` — registra un documento a través de `add_document_to_db`
   - `list_documents(chat_id, user_email)` / `delete_document(doc_id, user_email)` — gestión de documentos
   - `add_message` / `get_chat_history` — lectura/escritura del historial de chat
   - `add_sources_to_message` — adjuntar citas a un mensaje almacenado
   - `extract_text_from_url(url)` — obtener y devolver el contenido de texto de una URL
   - `execute_database_query(query, params)` — paso de SQL en bruto (ver nota de seguridad a continuación)
3. `ingest_document` no bloquea en la fragmentación — llama a `chunk_document.remote(text, chunk_size, doc_id)`, una tarea remota de Ray, por lo que los documentos grandes se procesan de manera asíncrona mientras la llamada a la herramienta devuelve inmediatamente.
4. Ejecutar `python backend/mcp/mcp_server.py` inicia `mcp.run()`, que sirve estas herramientas a través del transporte stdio de MCP — listo para que un cliente MCP se inicie y se conecte.
5. Un cliente MCP (por ejemplo, Claude Desktop) configurado para lanzar este script obtiene acceso automáticamente a las nueve herramientas, sin necesidad de escribir ningún código de integración específico de Panacea.

### Nota de seguridad

`execute_database_query` ejecuta una cadena SQL arbitraria contra la conexión de producción sin lista de permitidos o restricción de solo lectura — las consultas `SELECT` devuelven filas como JSON, cualquier otra cosa se compromete y devuelve el conteo de filas afectadas. Trata esto como territorio de privilegio mínimo: si expones este servidor a un cliente MCP en el que no confías completamente, ya sea elimina esta herramienta o limita su usuario de DB a acceso solo de lectura en tablas no sensibles.

## Ejecútalo localmente

Desde la raíz del espacio de trabajo (`anote/panacea`):

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build   # inicia MySQL, Redis, Tika y el backend
```

El servidor MCP necesita `fastmcp` (actualmente no está fijado en `backend/requirements.txt` — instálalo por separado) y `ray>=2.9.0` (ya está en `backend/requirements.txt`):

```bash
pip install fastmcp
cd Panacea/backend
python mcp/mcp_server.py
```

### Conectar un cliente MCP

Apunta un cliente compatible con MCP al script, por ejemplo, en el `claude_desktop_config.json` de Claude Desktop:

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

Reinicia el cliente, y las nueve herramientas anteriores estarán disponibles para invocar desde el chat.

## Notas para el libro de recetas

Buena continuación de la receta 04 — contrasta el registro de herramientas internas (`register_tool()` dentro del orquestador) con esta superficie externa de MCP. También vale la pena señalar como una brecha para los lectores: `fastmcp` aún no está listado en `backend/requirements.txt`, por lo que necesita una instalación manual hasta que eso se solucione en upstream.
