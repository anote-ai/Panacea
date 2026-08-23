# 설치

## CLI

```bash
npm install -g @anote-ai/anote
```

Node.js 18 이상이 필요합니다.

## VS Code 확장

VS Code 확장 마켓플레이스에서 **"Anote"**를 검색하거나 다음을 통해 설치합니다:

```bash
code --install-extension anote-ai.anote-ai-coding
```

## 웹 앱 (자체 호스팅)

```bash
git clone https://github.com/anote-ai/Panacea
cd Panacea
cp packages/backend/.env.example packages/backend/.env
# .env 파일을 API 키로 수정하세요
docker compose up
```

프론트엔드: http://localhost:3000 · 백엔드: http://localhost:5000

## 데스크탑 앱

[GitHub Releases](https://github.com/anote-ai/Panacea/releases)에서 최신 릴리스를 다운로드하세요.

사용 가능: **macOS** (DMG), **Windows** (설치 프로그램), **Linux** (AppImage/DEB/RPM).

## Python SDK

```bash
pip install anote-ai
```

## TypeScript/JavaScript SDK

```bash
npm install @anote-ai/sdk
```
