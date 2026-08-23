# Panacea 다중 모달 문서 수집

이 레시피는 Panacea가 문서 Q&A + RAG(자세한 내용은 [레시피 03](03-panacea-document-qa-rag.md))를 일반 텍스트를 넘어 이미지, 오디오, 비디오 및 스프레드시트로 확장하는 방법을 설명합니다. 이를 통해 모든 형식이 동일한 청크 및 임베딩 파이프라인을 통해 검색 가능하게 됩니다.

## 배울 내용

- Panacea가 MIME 유형에 따라 업로드를 분류하고 전용 수집 서비스로 라우팅하는 방법
- 이미지와 비디오 프레임이 비전 기능이 있는 LLM을 사용하여 인덱스 가능한 텍스트로 변환되는 방법
- 오디오(비디오의 오디오 트랙 포함)가 Whisper로 전사되는 방법
- 스프레드시트가 검색할 수 없는 텍스트 덤프가 아닌 Markdown 테이블로 변환되는 방법
- 다중 모달 수집을 관리하는 기능 플래그 및 크기 제한

## 왜 이것이 중요한가

Tika(기본 문서 텍스트 추출기)는 텍스트 기반 형식만 유용하게 처리할 수 있습니다. 추가 처리가 없으면 업로드된 이미지, 오디오 클립, 비디오 또는 스프레드시트는 수집에 실패하거나 모든 구조를 잃게 됩니다. 대신 Panacea는 업로드 시 미디어 유형을 감지하고 깨끗한 텍스트를 생성하는 목적에 맞는 서비스를 호출하여 이를 `document_text`로 저장하고 다른 문서와 동일한 검색 경로를 통해 흐르게 합니다. 따라서 스크린샷, 통화 녹음 또는 판매 스프레드시트는 PDF처럼 채팅을 통해 답변할 수 있게 됩니다.

## 주요 Panacea 파일

| 파일 | 중요성 |
|---|---|
| `Panacea/backend/api_endpoints/documents/handler.py` | 업로드 시 MIME 유형/확장자를 감지하고 올바른 수집 서비스로 라우팅 |
| `Panacea/backend/services/vision_service.py` | `describe_image()` — GPT-4o 또는 Claude 비전을 사용하여 이미지에 대한 자세한 텍스트 설명을 생성 |
| `Panacea/backend/services/audio_service.py` | `transcribe_audio()` — OpenAI Whisper로 오디오를 전사 |
| `Panacea/backend/services/video_service.py` | `ffmpeg`로 프레임을 추출하고, 비전 서비스로 각 프레임을 설명하며, 오디오 트랙을 별도로 전사하고 두 가지를 하나의 타임스탬프가 있는 문서로 결합 |
| `Panacea/backend/services/tabular_service.py` | `ingest_tabular()` — CSV/TSV/XLSX/XLS/ODS를 헤더와 행을 유지하는 Markdown 테이블로 변환 |
| `Panacea/backend/agents/config.py` | `AgentConfig` 기능 플래그: `ENABLE_MULTIMODAL`, `MAX_IMAGE_BYTES`, `MAX_AUDIO_BYTES`, `MAX_VIDEO_BYTES`, `VIDEO_FRAME_INTERVAL_SECS`, `VIDEO_MAX_FRAMES` |

## 작동 방식

1. 파일은 일반 문서에 사용되는 동일한 엔드포인트를 통해 업로드됩니다. `handler.py`는 MIME 유형/확장자를 감지하여 이미지를, 비디오, 오디오, 표 형식 또는 일반 텍스트/문서로 분류합니다.
2. **이미지** → `vision_service.describe_image()`는 이미지를(base64 인코딩) 비전 기능이 있는 모델에 전송하고, 보이는 텍스트를 전사하고, 차트/다이어그램/UI 스크린샷을 설명하며, 객체와 레이아웃을 주목하라는 프롬프트를 제공합니다. 따라서 설명만으로도 의미 검색이 나중에 이를 찾을 수 있습니다.
3. **오디오** → `audio_service.transcribe_audio()`는 Whisper(`whisper-1`)를 호출하고 지속 시간/언어 메타데이터가 포함된 전사본을 반환합니다.
4. **비디오** → `video_service`는 고정 간격(`VIDEO_FRAME_INTERVAL_SECS`, 기본 30초, `VIDEO_MAX_FRAMES`로 제한)으로 `ffmpeg`를 사용하여 프레임을 추출하고, 비전 서비스로 각 프레임을 설명하며, 오디오 트랙을 별도로 전사하고 두 가지를 하나의 타임스탬프가 있는 문서로 결합합니다.
5. **표 형식** → `tabular_service.ingest_tabular()`는 각 시트를 네이티브로 파싱( `csv`/`pandas`+`openpyxl`/`xlrd`를 통해)하고 Markdown 테이블로 렌더링하며, 첫 번째 500개 행을 초과하는 경우 일반 CSV로 대체하여 검색 인덱스에서 손실되지 않도록 합니다.
6. 이러한 서비스에서 나오는 모든 텍스트는 `document_text`로 저장되고 일반 문서와 정확히 같은 방식으로 청크 및 임베딩되어, 레시피 03의 표준 RAG Q&A 흐름을 통해 검색할 수 있습니다.

모든 서비스는 **결코 오류를 발생시키지 않도록** 설계되었습니다. 실패한 비전 호출, 누락된 종속성 또는 과도한 파일은 자리 표시자 문자열(예: `"[이미지가 인라인 분석을 위해 너무 큽니다 (23.4 MB). 제한: 20 MB.]"`)을 반환하므로 문서 레코드는 항상 생성되고 전체 업로드가 실패하지 않습니다.

## 로컬에서 실행하기

작업 공간 루트(`anote/panacea`)에서:

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

다중 모달 수집은 기본적으로 활성화되어 있습니다(`ENABLE_MULTIMODAL=true`). 동작을 조정하려면 `backend/.env`에서 다음을 설정하십시오:

```bash
ENABLE_MULTIMODAL=true        # 마스터 스위치
MAX_IMAGE_BYTES=20971520      # 기본 20 MB
MAX_AUDIO_BYTES=26214400      # 기본 25 MB
MAX_VIDEO_BYTES=524288000     # 기본 500 MB
VIDEO_FRAME_INTERVAL_SECS=30
VIDEO_MAX_FRAMES=20
```

비디오 수집은 추가로 `ffmpeg`가 백엔드 컨테이너의 `PATH`에 있어야 합니다(제공된 Docker 이미지에 이미 포함되어 있음). Excel 수집은 `openpyxl`(XLSX/ODS) 및 `xlrd`(구형 XLS)가 필요하며, 두 비전/오디오 서비스는 `DEFAULT_AGENT_MODEL_TYPE`에 따라 `OPENAI_API_KEY` 및/또는 `ANTHROPIC_API_KEY`를 설정해야 합니다.

### 시도해 보기

```bash
curl -X POST http://localhost:5000/ingest-pdf \
  -F chat_id=1 \
  -F "files[]=@./screenshot.png"

curl -X POST http://localhost:5000/ingest-pdf \
  -F chat_id=1 \
  -F "files[]=@./quarterly_sales.xlsx"
```

그런 다음 `http://localhost:3000`의 웹 UI에서 동일한 채팅 세션을 열고 방금 업로드한 이미지나 스프레드시트에 대한 질문을 하십시오. Panacea는 생성된 설명/Markdown 테이블에서 PDF처럼 정확하게 답변합니다.

## 요리책을 위한 노트

이 레시피는 레시피 03과 잘 어울립니다: 동일한 RAG 파이프라인이지만 입력 형식의 폭이 더 넓습니다. 독자에게 "인덱스 품질"이 이미지/비디오에 대해 비전 모델의 설명만큼 좋다는 점을 강조할 가치가 있으며, `vision_service.py`의 `_INDEXING_PROMPT`에서 프롬프트 조정은 자연스러운 사용자 정의 지점입니다.
