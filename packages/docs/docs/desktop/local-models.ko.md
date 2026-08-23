# 로컬 모델

데스크탑 앱은 [Ollama](https://ollama.ai)를 통해 로컬 LLM 추론을 지원합니다.

## 설정

1. [ollama.ai](https://ollama.ai)에서 Ollama를 설치합니다.
2. 모델을 가져옵니다:
   ```bash
   ollama pull llama3
   ollama pull mistral
   ```
3. 데스크탑 앱에서 모델 드롭다운에서 로컬 모델을 선택합니다 (`ollama/`로 접두사가 붙음)

## 지원되는 모델

| 모델 | 가져오기 명령 |
|-------|--------------|
| Llama 3 | `ollama pull llama3` |
| Mistral | `ollama pull mistral` |
| Phi-3 | `ollama pull phi3` |

로컬 모델은 완전히 귀하의 하드웨어에서 실행됩니다 — 데이터가 귀하의 기기를 떠나지 않습니다.
