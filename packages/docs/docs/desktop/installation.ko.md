# 데스크탑 앱 설치

## 다운로드

GitHub 릴리스 페이지에서 플랫폼에 맞는 최신 릴리스를 다운로드하세요.

| 플랫폼 | 파일 |
|--------|------|
| macOS | `Anote-AI-x.x.x.dmg` |
| Windows | `Anote-AI-Setup-x.x.x.exe` |
| Linux (deb) | `anote-ai_x.x.x_amd64.deb` |

## 소스에서 빌드하기

```bash
# 1. Python 백엔드 번들링
cd packages/backend
pip install pyinstaller
pyinstaller ../desktop/app.spec --distpath ../desktop/backend-dist

# 2. Electron 앱 빌드 및 패키징
cd packages/desktop
npm install
npm run make
```

패키징된 앱은 `packages/desktop/out/`에 있습니다.
