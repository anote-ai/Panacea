# 변경 로그

Panacea는 아직 수동으로 유지 관리되는 변경 로그 파일을 게시하지 않습니다 — 배포된 내용의 진실한 출처는 다음과 같습니다:

- **[GitHub 릴리스](https://github.com/anote-ai/Panacea/releases)** — CLI, VS Code 확장 및 기타 패키지에 대한 태그 릴리스
- **[커밋 기록](https://github.com/anote-ai/Panacea/commits/main)** — 모든 변경 사항, 순서대로

## 자신의 프로젝트에 대한 변경 로그 생성

CLI는 *당신의* 코드베이스에 대한 git 기록에서 변경 로그를 작성할 수 있습니다:

```bash
anote changelog                    # 마지막 태그 이후
anote changelog --since v1.2.0
anote changelog --dry-run          # CHANGELOG.md를 작성하는 대신 출력
```

이것은 Panacea가 아닌 당신의 프로젝트의 `CHANGELOG.md`에 기록됩니다.
