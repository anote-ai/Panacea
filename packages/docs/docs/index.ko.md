# 개요

**Anote AI**는 통합 AI 코딩 어시스턴트이자 프라이빗 채팅 플랫폼입니다. 코드베이스를 읽고, 파일을 편집하고, 명령을 실행하고, 풀 리퀘스트를 검토하고, 문서에 대한 질문에 답합니다 — 터미널, IDE, 브라우저, 데스크톱 앱, 휴대폰에서 사용할 수 있습니다.

## 시작하기

Anote는 여러 서피스에서 실행됩니다: CLI, VS Code, 웹, 데스크톱, 모바일. 아래에서 하나를 선택해 시작하세요. 대부분의 서피스는 호스팅된 Anote 백엔드 또는 자체 호스팅 인스턴스와 통신합니다([설정](getting-started/configuration.md) 참조).

=== "CLI"

    터미널에서 직접 Anote와 함께 작업할 수 있는 완전한 기능의 CLI입니다. 질문하고, 버그를 수정하고, 풀 리퀘스트를 검토하고, 셸을 벗어나지 않고 코드베이스를 검색할 수 있습니다.

    ```bash
    npm install -g @anote-ai/anote
    ```

    Node.js 18 이상이 필요합니다. 그런 다음 어떤 프로젝트에서든:

    ```bash
    cd your-project
    anote init
    anote ask "explain this codebase"
    ```

    `anote init`은 API 키와 선호하는 LLM 제공업체 설정을 안내합니다.

    [빠른 시작으로 계속하기 →](getting-started/quickstart.md)

=== "VS Code"

    VS Code 확장 프로그램은 채팅 사이드바, 인라인 diff 검토, 스트리밍 응답을 편집기에 직접 제공합니다.

    VS Code 확장 마켓플레이스에서 **"Anote"**를 검색하거나 다음으로 설치하세요:

    ```bash
    code --install-extension anote-ai.anote-ai-coding
    ```

    [VS Code 확장 프로그램 개요 →](vscode/overview.md)

=== "웹 앱"

    문서 업로드와 RAG 기반 Q&A를 지원하는 ChatGPT 스타일의 브라우저 채팅 인터페이스입니다. Docker Compose로 셀프 호스팅하세요:

    ```bash
    git clone https://github.com/anote-ai/Panacea
    cd Panacea
    cp packages/backend/.env.example packages/backend/.env
    # API 키로 .env 편집
    docker compose up
    ```

    프론트엔드: `http://localhost:3000` · 백엔드: `http://localhost:5000`

    [웹 앱 개요 →](web/overview.md)

=== "데스크톱"

    프라이빗하고 오프라인 사용이 가능한 Electron 앱입니다. 모든 데이터는 사용자의 컴퓨터에 남아 있으며, 호스팅된 제공업체를 사용하고 싶지 않을 때 로컬 Ollama 모델과 함께 작동합니다.

    [GitHub Releases](https://github.com/anote-ai/Panacea/releases)에서 최신 버전을 다운로드하세요 — **macOS**(DMG), **Windows**(설치 프로그램), **Linux**(AppImage/DEB/RPM)를 지원합니다.

    [데스크톱 앱 개요 →](desktop/overview.md)

=== "모바일"

    Expo로 빌드된 네이티브 iOS 및 Android 채팅 클라이언트입니다.

    ```bash
    cd packages/mobile
    npm install
    npx expo start
    ```

    Expo Go 앱으로 QR 코드를 스캔하거나 시뮬레이터에서 실행하세요.

    [모바일 앱 개요 →](mobile/overview.md)

## 할 수 있는 일

??? abstract "코드베이스에 대해 질문하기"

    ```bash
    anote ask "how does the authentication middleware work?"
    anote ask --file src/auth.ts "explain this file"
    anote ask --compare               # 여러 모델을 나란히 비교
    cat src/handler.py | anote ask "what could go wrong here?"
    ```

??? bug "버그 자동 수정하기"

    `anote fix --loop`는 테스트 스위트에 대해 반복 실행되며 — 최대 `--max-iterations` 라운드까지 — 통과할 때까지 실행되거나, `--file`로 단일 파일을 수정합니다.

    ```bash
    anote fix --loop --max-iterations 5
    ```

??? example "풀 리퀘스트 검토하기"

    ```bash
    anote review --pr 42
    ```

    버그, 보안 문제, 품질에 대한 검토 — 디렉터리/파일에 대해 로컬로, 또는 GitHub PR에 직접 게시됩니다.

??? search "코드베이스 시맨틱 검색하기"

    ```bash
    anote index              # TF-IDF 인덱스 구축(한 번 실행 후 최신 상태 유지)
    anote search "JWT token validation"
    ```

??? question "문서에 대해 채팅하고 질문하기"

    [웹 앱](web/overview.md) 또는 [데스크톱 앱](desktop/overview.md)에서 문서를 업로드하고 질문하세요 — `POST /api/documents/{id}/ask`를 통한 RAG 기반입니다.

??? tip "보안 및 성능 감사하기"

    ```bash
    anote security --severity high --fix
    anote perf --focus "database,bundle" --fix
    ```

??? note "변경 이력 및 문서 생성, 또는 마이그레이션 실행하기"

    ```bash
    anote changelog --since v1.2.0
    anote docs src/api.ts --style jsdoc
    anote migrate --from "React 17" --to "React 18"
    ```

??? info "설정 확인하기"

    ```bash
    anote doctor
    ```

    Node.js ≥ 18, `ANTHROPIC_API_KEY`, `.anote.json`, `CLAW.md`, git을 확인합니다.

## 어디서나 Anote 사용하기

| 하고 싶은 것 | 최선의 선택 |
|---|---|
| 터미널에서 작업하기 | [CLI](cli/overview.md) |
| 편집기에서 바로 AI 도움받기 | [VS Code 확장 프로그램](vscode/overview.md) |
| 브라우저에서 문서와 채팅하기 | [웹 앱](web/overview.md) |
| 모든 것을 프라이빗하고 오프라인으로 유지하기 | [데스크톱 앱](desktop/overview.md) — 로컬 Ollama 모델과 함께 작동 |
| 휴대폰에서 채팅하기 | [모바일 앱](mobile/overview.md) |
| 내 코드나 스크립트에서 Anote 호출하기 | [TypeScript SDK](sdk/typescript.md) 또는 [Python SDK](sdk/python.md) |
| REST API에 직접 통합하기 | [백엔드 API](api/overview.md) |
| PR 검토 또는 CI 검사 자동화하기 | [CLI: `anote review --pr`](cli/commands.md#anote-review) |

## 지원되는 LLM 제공업체

- **Anthropic** — Claude(`claude-opus-4-8`, `claude-sonnet-4-6`, `claude-haiku-4-5`)
- **OpenAI** — GPT-4o, GPT-4o-mini
- **Google** — Gemini 2.0 Flash, Gemini 1.5 Pro
- **Ollama** — 모든 로컬 모델(Llama 3, Mistral 등)
- **xAI** — Grok

## 다음 단계

- [빠른 시작](getting-started/quickstart.md) — init, ask, fix, index, review, changelog 순서대로
- [Panacea 작동 방식](core-concepts/how-it-works.md) — 에이전트 루프, 도구, 스트리밍
- [권한 모드](use-panacea/permission-modes.md) — 에이전트가 묻지 않고 할 수 있는 작업 제어
- [일반적인 워크플로우](use-panacea/common-workflows.md) — 일상 작업을 위한 단계별 패턴
- [설정](getting-started/configuration.md) — API 키, 제공업체 설정, `~/.anote/config.json`
- [CLI 명령어](cli/commands.md) — 전체 명령어 참조
- [백엔드 API](api/overview.md) — 모든 서피스를 지원하는 REST 엔드포인트
- [아키텍처](development/architecture.md) — 모노레포와 백엔드가 어떻게 맞물리는지
- [기여하기](development/contributing.md) — 로컬 개발을 위한 저장소 설정
