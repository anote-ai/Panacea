# Python SDK

Python 클라이언트는 `anoteai` 패키지를 통해 사용할 수 있습니다 (Anote-Product 리포지토리의 일부).

## 설치

```bash
pip install anoteai
```

## 사용법

```python
from anoteai import Anote

client = Anote(api_key="sk-ai-...")

# 기존의 공개 메서드는 Authorization: Bearer sk-ai-...로 인증합니다.
result = client.classify(document_id="doc_123", labels=["contract", "invoice"])
answer = client.answer(document_id="doc_123", question="지불 금액은 얼마입니까?")
```

API 키는 설정 -> API 키에서 생성할 수 있습니다. 평문 키는 한 번만 표시되며, 그 이후에는 키 접두사만 표시됩니다.

크레딧 비용:

| 작업 | 크레딧 |
| --- | ---: |
| 문서 업로드 | 파일 또는 URL당 1 |
| 채팅 메시지 / Q&A | 요청당 1 |
| OpenAI 호환 채팅 완료 | 요청당 1 |

상태 코드로 API 오류 처리:

| 상태 | 의미 |
| --- | --- |
| 401 | API 키가 누락되었거나 유효하지 않음 |
| 402 | 크레딧 부족 |
| 429 | 키당 비율 제한 초과 |

전체 SDK 문서는 [Anote-Product 리포지토리](https://github.com/anote-ai/anote-product)를 참조하십시오.
