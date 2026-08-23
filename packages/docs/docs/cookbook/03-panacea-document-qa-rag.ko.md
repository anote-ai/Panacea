# Panacea 문서 Q&A + RAG

이 레시피는 Panacea가 검색 보강 생성(RAG)을 사용하여 개인 문서 질문 응답을 구축하는 방법을 설명합니다.

## 배울 내용

- Panacea가 문서를 수집하고 검색 가능한 텍스트로 저장하는 방법
- 백엔드가 질문에 대한 관련 청크를 검색하는 방법
- 시스템이 임베딩 및 문서 소스를 사용하여 답변을 근거하는 방법
- Q&A 피드백이 어떻게 수집되고 향후 응답을 개선하는지

## 왜 이것이 중요한가

Panacea는 팀이 개인 문서에 대해 질문할 수 있도록 설계되었으며, 이를 제3자 채팅 서비스에 전송하지 않습니다. 워크플로우는 다음과 같습니다:

1. 문서 업로드
2. 콘텐츠 청크 및 임베딩
3. 사용자 쿼리에 대한 관련 청크 검색
4. 인용과 함께 LLM을 사용하여 답변
5. 품질 개선을 위한 피드백 수집

## 주요 Panacea 파일

| 파일 | 중요성 |
|---|---|
| `Panacea/backend/api_endpoints/documents/handler.py` | 문서 업로드 및 수집 API 경로 |
| `Panacea/backend/database/db.py` | 문서 저장 및 검색 SQL 로직 |
| `Panacea/backend/database/qa_feedback.py` | 문서 Q&A에 대한 피드백 수집 |
| `Panacea/backend/agents/multi_agent_system.py` | 다중 에이전트 워크플로우에서 사용되는 문서 검색 에이전트 |

## 작동 방식

- 문서는 백엔드를 통해 업로드되고 `documents.document_text`에 저장됩니다.
- 시스템은 대형 문서를 청크로 나누고 빠른 조회를 위한 검색 메타데이터를 생성합니다.
- 사용자가 질문을 하면 Panacea는 최상의 청크를 검색하기 위해 하나 이상의 전문 에이전트를 선택하고 답변을 생성합니다.
- 결과에는 사용자가 원본 문서로 답변을 추적할 수 있도록 하는 출처 인용이 포함됩니다.
- 피드백 신호는 향후 품질 개선을 가능하게 하기 위해 `qa_feedback`에 기록됩니다.

## 로컬에서 실행하기

작업 공간 루트(`anote/panacea`)에서:

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

이 명령은 백엔드, 웹 앱, MySQL, Redis 및 Tika를 시작합니다.

이미 레시피 폴더 안에 있는 경우, 다음을 사용하세요:

```bash
cd ../../../Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

`http://localhost:3000`을 열어 Panacea 웹 UI를 사용하세요. 문서 업로드는 필수 양식 필드 `chat_id` 및 `files[]`와 함께 백엔드 경로 `POST /ingest-pdf`에 의해 처리됩니다.

예제 업로드 명령:

```bash
curl -X POST http://localhost:5000/ingest-pdf \
  -F chat_id=1 \
  -F "files[]=@./path/to/document.pdf"
```

### 최소 업로드 절차

1. 레포지토리 루트에서 Panacea 시작:

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

2. 다른 터미널에서 단일 텍스트 또는 PDF 문서 업로드:

```bash
curl -X POST http://localhost:5000/ingest-pdf \
  -F chat_id=1 \
  -F "files[]=@./Cookbook/recipes/03-panacea-document-qa-rag/data/sample-doc.txt"
```

3. 백엔드가 성공적인 `Document Uploaded` 응답을 반환하는지 확인합니다.

4. `http://localhost:3000`에서 웹 UI를 사용하고 동일한 채팅 세션을 선택하여 업로드된 문서에 대한 질문을 합니다.

업로드 후 API를 직접 테스트하고 싶다면, UI 또는 데이터베이스에서 채팅 세션 ID를 찾아 앱의 채팅 흐름을 통해 질문을 보내세요. Panacea는 관련 청크를 검색하고 근거 있는 답변을 생성합니다.

## 요리책을 위한 노트

이 레시피는 Panacea가 개인 지식 작업을 지원하는 방법을 설명하는 요리책 항목에 이상적입니다. 이는 단일 스크립트보다 개념적이며, 실제 가치는 문서 수집 및 검색 아키텍처를 이해하는 데 있습니다.
