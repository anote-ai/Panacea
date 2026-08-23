# 行動應用程式概覽

Anote AI 行動應用程式是使用 [Expo](https://expo.dev) 和 React Native 建置的。

## 功能

- 原生 iOS 和 Android 支援
- 明亮/黑暗模式（遵循系統偏好設定）
- 具串流回應的聊天介面
- 帶有滑入側邊欄的會話歷史
- 透過 `expo-secure-store` 安全儲存 JWT

## 本地運行

```bash
cd packages/mobile
npm install
npx expo start
```

使用 Expo Go 應用程式掃描 QR 碼或在模擬器中運行。

## 配置

透過環境變數設置 API URL：

```bash
EXPO_PUBLIC_API_URL=https://api.anote.ai npx expo start
```
