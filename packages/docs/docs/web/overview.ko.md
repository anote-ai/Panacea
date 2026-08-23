# 웹 앱 개요

Anote AI 웹 앱은 Anote 백엔드에 연결되는 ChatGPT 스타일의 채팅 인터페이스입니다.

## 기능

- 라이트 및 다크 모드 (시스템 기본 설정 자동 감지)
- SSE를 통한 스트리밍 응답
- 접을 수 있는 사이드바에 채팅 세션 기록
- 모델 선택기 (Claude, GPT-4o 등)
- 문서 업로드 및 Q&A
- 반응형 디자인

## 로컬에서 실행하기

```bash
cd packages/web
npm install
npm run dev
```

앱은 `http://localhost:3000`에서 실행되며 API 호출을 `http://localhost:5000`으로 프록시합니다.
