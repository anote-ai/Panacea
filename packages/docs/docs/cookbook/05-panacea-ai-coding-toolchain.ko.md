# Panacea AI 코딩 툴체인

이 레시피는 Panacea의 AI 코딩 경험이 CLI, SDK 및 VS Code를 통해 어떻게 제공되는지를 설명합니다.

## 배울 내용

- Panacea의 다양한 AI 코딩 진입점
- CLI, SDK 및 VS Code 확장이 공유 백엔드와 어떻게 관련되는지
- 개인 코드 지원을 위한 주요 제품 기능
- 구현 세부정보를 찾기 위한 레포지토리 위치

## 왜 중요한가

Panacea는 여러 인터페이스를 갖춘 통합 제품으로 구축되었습니다:

- `anote chat`, 코드 검색 및 레포 리뷰를 지원하는 **CLI**
- 편집기 내 AI 지원을 위한 **VS Code 확장**
- 다른 애플리케이션에 Panacea를 임베드하기 위한 **SDK**

이 인터페이스들은 백엔드와 에이전트 기반 추론 레이어를 공유하여 데스크탑, 웹 및 코드 워크플로우 전반에 걸쳐 일관된 제품을 만듭니다.

## 주요 Panacea 파일

| 파일 | 중요성 |
|---|---|
| `Panacea/packages/cli` | 개발자 워크플로우를 위한 TypeScript CLI 구현 |
| `Panacea/packages/vscode` | VS Code 확장 및 채팅 통합 |
| `Panacea/packages/sdk` | 프로그래밍적 접근을 위한 TypeScript SDK |
| `Panacea/packages/backend` | 모든 UI 및 CLI 상호작용을 지원하는 공유 백엔드 서비스 |

## 작동 방식

- 코딩 사용자 작업은 CLI, SDK 또는 VS Code 확장에서 시작됩니다.
- 요청은 Panacea의 백엔드 API로 전송됩니다.
- 백엔드는 에이전트 조정 및 모델 제공자를 사용하여 코드 인식 답변을 생성합니다.
- 응답은 동일한 인터페이스로 반환되며, 코드 제안, 설명 또는 수정 사항이 포함됩니다.

## 유용한 제품 기능

- **CLI**: `anote chat`, 레포 검색, 코드 리뷰, 코드 생성 및 임베딩 기반 지원.
- **VS Code**: 인라인 채팅, 차이 미리보기, 코드 작업 및 스트리밍 응답.
- **SDK**: Panacea API를 위한 클라이언트 래퍼로, 사용자 정의 통합을 가능하게 합니다.

## 로컬에서 실행하기

작업 공간 루트(`anote/panacea`)에서:

```bash
cd Panacea
cp packages/backend/.env.example packages/backend/.env
docker compose up --build
```

이 명령은 공유 백엔드 및 프론트엔드 서비스를 시작합니다.

다른 터미널에서 CLI 패키지를 실행합니다:

```bash
cd Panacea/packages/cli
npm install
npm run dev
```

그런 다음 CLI를 로컬에서 사용하거나 `npm run build`로 빌드할 수 있습니다.

VS Code 개발을 위해 `Panacea/packages/vscode`를 VS Code에서 열고 디버거로 확장을 실행합니다.

## 요리책을 위한 노트

이 레시피는 Panacea의 다중 인터페이스 AI 코딩 제품에 대한 높은 수준의 워크스루가 필요한 팀원들에게 유용합니다. 또한 독자들이 수정하거나 확장할 수 있는 구현 파일을 찾도록 안내할 수 있습니다.
