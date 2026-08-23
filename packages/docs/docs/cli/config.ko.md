# CLI 구성

Anote CLI는 프로젝트 루트의 `.anote.json` 또는 전역적으로 `~/.anote/config.json`을 통해 구성할 수 있습니다.

## 구성 파일

```json
{
  "model": "claude-sonnet-4-6",
  "permissionMode": "default",
  "maxTurns": 20,
  "provider": "anthropic"
}
```

## 구성 관리

```bash
anote config list          # 모든 설정 표시
anote config get model     # 값 가져오기
anote config set model claude-haiku-4-5-20251001  # 값 설정
anote config unset model   # 값 제거
```
