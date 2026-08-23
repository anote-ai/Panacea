# Panacea MCP 도구 서버

이 레시피는 Panacea가 문서/채팅 원시 기능을 표준 [모델 컨텍스트 프로토콜](https://modelcontextprotocol.io/) (MCP) 도구로 노출하는 방법을 설명합니다. 따라서 모든 MCP 호환 클라이언트(Claude Desktop, 기타 MCP 호스트)는 Panacea의 검색 및 채팅 기록 기능을 직접 사용할 수 있습니다.

## 배울 내용

- 이 MCP 인터페이스와 레시피 04의 내부 에이전트/도구 등록 아키텍처 간의 차이
- MCP 도구로 노출된 문서 및 채팅 작업
- 문서 수집이 Ray 원격 작업을 통해 비차단 방식으로 유지되는 방법
- 원시 SQL 패스스루 도구가 주목할 만한 보안 고려 사항인 이유

## 왜 이것이 중요한가

레시피 04는 Panacea의 *내부* 오케스트레이터가 도구를 등록하여 자신의 에이전트가 호출하도록 하는 방법을 다룹니다. 이는 다른 통합 인터페이스로, 동일한 기본 문서/채팅 기능을 **외부, 표준화된 MCP 도구**로 패키징하여 모든 MCP 클라이언트가 호출할 수 있도록 합니다 — Panacea 전용 SDK나 API 계약이 필요 없으며, 단지 MCP 프로토콜만 필요합니다.

## 주요 Panacea 파일

| 파일 | 중요성 |
|---|---|
| `Panacea/backend/mcp/mcp_server.py` | `FastMCP("Document Agent Server")` — 아홉 개의 MCP 도구를 정의 |
| `Panacea/backend/api_endpoints/financeGPT/chatbot_endpoints.py` | 각 MCP 도구가 래핑하는 기본 DB-facing 함수들 (`get_relevant_chunks`, `add_document_to_db`, `chunk_document` 등) |
| `Panacea/backend/database/db.py` | `get_db_connection` — `execute_database_query` 도구에서 직접 사용 |

## 작동 방식

1. `mcp_server.py`는 Ray를 초기화하고 (`ray.init(...)`) `"Document Agent Server"`라는 이름의 `FastMCP` 서버 인스턴스를 생성합니다.
2. `@mcp.tool()`로 장식된 각 함수는 기존 Panacea 함수를 래핑하고 일반 텍스트 결과 또는 오류 문자열을 반환합니다 — LLM 도구 호출이 기대하는 형태:
   - `retrieve_relevant_chunks(query, chat_id, user_email, k=2)` — `get_relevant_chunks`를 통한 채팅 문서에 대한 의미 검색
   - `ingest_document(text, document_name, chat_id, chunk_size=1000)` — `add_document_to_db`를 통해 문서 등록
   - `list_documents(chat_id, user_email)` / `delete_document(doc_id, user_email)` — 문서 관리
   - `add_message` / `get_chat_history` — 채팅 기록 읽기/쓰기
   - `add_sources_to_message` — 저장된 메시지에 인용 추가
   - `extract_text_from_url(url)` — URL에서 텍스트 콘텐츠를 가져와 반환
   - `execute_database_query(query, params)` — 원시 SQL 패스스루 (아래 보안 참고 사항 참조)
3. `ingest_document`는 청크화에서 차단되지 않습니다 — `chunk_document.remote(text, chunk_size, doc_id)`를 호출하여 Ray 원격 작업을 수행하므로 대형 문서는 비동기적으로 처리되며 도구 호출은 즉시 반환됩니다.
4. `python backend/mcp/mcp_server.py`를 실행하면 `mcp.run()`이 시작되어 MCP의 stdio 전송을 통해 이러한 도구를 제공합니다 — MCP 클라이언트가 시작하고 연결할 준비가 됩니다.
5. 이 스크립트를 실행하도록 구성된 MCP 클라이언트(예: Claude Desktop)는 Panacea 전용 통합 코드를 작성하지 않고도 자동으로 아홉 개의 도구에 접근할 수 있습니다.

### 보안 참고 사항

`execute_database_query`는 허용 목록이나 읽기 전용 제한 없이 프로덕션 연결에 대해 임의의 SQL 문자열을 실행합니다 — `SELECT` 쿼리는 JSON으로 행을 반환하고, 그 외의 쿼리는 커밋하고 영향을 받은 행 수를 반환합니다. 이를 최소 권한 영역으로 취급하십시오: 신뢰하지 않는 MCP 클라이언트에 이 서버를 노출하는 경우, 이 도구를 제거하거나 비민감 테이블에 대해 읽기 전용 접근으로 DB 사용자의 범위를 제한하십시오.

## 로컬에서 실행하기

작업 공간 루트(`anote/panacea`)에서:

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build   # MySQL, Redis, Tika 및 백엔드를 시작합니다.
```

MCP 서버는 `fastmcp`가 필요하며 (현재 `backend/requirements.txt`에 고정되어 있지 않음 — 별도로 설치해야 함) `ray>=2.9.0` (이미 `backend/requirements.txt`에 있음)이 필요합니다:

```bash
pip install fastmcp
cd Panacea/backend
python mcp/mcp_server.py
```

### MCP 클라이언트 연결

MCP 호환 클라이언트를 스크립트에 지정합니다. 예를 들어 Claude Desktop의 `claude_desktop_config.json`에서:

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

클라이언트를 재시작하면 위의 아홉 개 도구를 채팅에서 호출할 수 있게 됩니다.

## 요리책을 위한 노트

레시피 04에 대한 좋은 후속 작업입니다 — 내부 도구 등록(`register_tool()`이 오케스트레이터 내부에 있음)과 이 외부 MCP 인터페이스를 대조하십시오. 독자들에게 주목할 만한 격차로, `fastmcp`는 아직 `backend/requirements.txt`에 나열되지 않았으므로, 상위에서 수정될 때까지 수동 설치가 필요합니다.
