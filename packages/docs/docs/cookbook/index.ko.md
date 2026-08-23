# 요리책 개요

Panacea 요리책은 Panacea 플랫폼 기능이 어떻게 작동하는지를 보여주는 구현 가이드 모음입니다 — 문서 수집 및 RAG, 다중 에이전트 오케스트레이션, 청구, MCP 도구 서버 등. 각 가이드는 관련된 실제 백엔드 파일을 지목하고 시스템의 해당 부분을 로컬에서 실행하는 방법을 설명합니다.

출처: [anote-ai/Cookbook](https://github.com/anote-ai/Cookbook).

## 레시피

| 레시피 | 설명 |
|---|---|
| [문서 Q&A + RAG](03-panacea-document-qa-rag.md) | Panacea의 개인 문서 수집, 검색 및 근거 있는 답변 워크플로우 이해하기 |
| [다중 에이전트 오케스트레이션](04-panacea-multi-agent-orchestration.md) | Panacea가 작업을 오케스트레이터, 에이전트, 팀 및 워크플로우를 통해 라우팅하는 방법 배우기 |
| [AI 코딩 도구 체인](05-panacea-ai-coding-toolchain.md) | Panacea가 CLI, VS Code 및 SDK를 통해 코딩 지원을 제공하는 방법 탐색하기 |
| [다중 모달 문서 수집](06-panacea-multimodal-ingestion.md) | Panacea가 이미지, 오디오, 비디오 및 스프레드시트를 동일한 RAG 파이프라인을 통해 검색 가능하게 만드는 방법 이해하기 |
| [OpenAI 호환 API 게이트웨이](07-panacea-openai-compatible-gateway.md) | 코드 변경 없이 OpenAI-SDK 기반 도구를 Panacea에 연결하기 |
| [청구, API 키 및 요청당 크레딧 측정](08-panacea-billing-and-api-keys.md) | Stripe 구독, API 키 및 요청당 크레딧 측정이 어떻게 결합되는지 배우기 |
| [MCP 도구 서버](09-panacea-mcp-tool-server.md) | Panacea의 문서/채팅 기본 요소를 Claude Desktop 및 기타 MCP 클라이언트를 위한 표준 MCP 도구로 노출하기 |
| [다중 채널 메시징 봇](10-panacea-messaging-bots.md) | Slack, SMS 및 WhatsApp에서 Panacea 코딩 질문하기 |

## 레시피를 로컬에서 실행하기

대부분의 레시피는 전체 Panacea 스택에 대해 실행됩니다:

```bash
cp packages/backend/.env.example packages/backend/.env
docker compose up --build
```

전체 설정을 보려면 [시작하기](../getting-started/installation.md)를 참조하고, 각 레시피의 특정 실행 단계는 해당 페이지를 참조하세요.
