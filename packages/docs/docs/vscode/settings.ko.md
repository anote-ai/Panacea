# VS Code 확장 설정

VS Code의 설정 UI 또는 `settings.json`에서 확장을 구성합니다.

| 설정 | 기본값 | 설명 |
|------|--------|------|
| `anote.model` | `claude-sonnet-4-6` | 사용할 기본 모델 |
| `anote.apiKey` | `""` | Anthropic API 키 (또는 env var 사용) |
| `anote.permissionMode` | `default` | 도구 권한 모드: `default`, `auto`, `manual` |
| `anote.showToolUse` | `true` | 채팅 패널에 도구 호출 표시 |

```json
{
  "anote.model": "claude-sonnet-4-6",
  "anote.permissionMode": "default"
}
```
