# 구성

## CLI 구성

구성은 `~/.anote/config.json`에 저장됩니다:

```json
{
  "model": "claude-sonnet-4-6",
  "provider": "anthropic",
  "apiKey": "sk-ant-...",
  "serverUrl": "http://localhost:5000",
  "maxTurns": 30,
  "permissionMode": "default"
}
```

다음 명령어로 관리할 수 있습니다:

```bash
anote config set model claude-opus-4-8
anote config get model
anote config list
```

## 환경 변수

모든 설정은 환경 변수로 재정의할 수 있습니다:

| 변수 | 목적 |
|---|---|
| `ANTHROPIC_API_KEY` | Anthropic API 키 |
| `OPENAI_API_KEY` | OpenAI API 키 |
| `GEMINI_API_KEY` | Google Gemini API 키 |
| `ANOTE_MODEL` | 기본 모델 |
| `ANOTE_SERVER_URL` | Anote 백엔드 URL |

## 백엔드 구성

`packages/backend/.env.example`을 `packages/backend/.env`로 복사하고 다음을 입력합니다:

```bash
# LLM 제공자
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...

# 데이터베이스
DB_HOST=localhost
DB_NAME=anote
DB_USER=anote
DB_PASSWORD=anote

# 인증
JWT_SECRET_KEY=your-secret-key

# 결제 (선택 사항)
STRIPE_SECRET_KEY=sk_...
```
