# 모바일 앱 개요

Anote AI 모바일 앱은 [Expo](https://expo.dev)와 React Native로 구축되었습니다.

## 기능

- 네이티브 iOS 및 Android 지원
- 라이트/다크 모드 (시스템 기본 설정 따름)
- 스트리밍 응답이 있는 채팅 인터페이스
- 슬라이드 인 사이드바가 있는 세션 기록
- `expo-secure-store`를 통한 안전한 JWT 저장

## 로컬 실행

```bash
cd packages/mobile
npm install
npx expo start
```

Expo Go 앱으로 QR 코드를 스캔하거나 시뮬레이터에서 실행하세요.

## 구성

환경 변수를 통해 API URL을 설정하세요:

```bash
EXPO_PUBLIC_API_URL=https://api.anote.ai npx expo start
```
