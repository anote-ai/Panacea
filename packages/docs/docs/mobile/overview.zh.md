# 移动应用概述

Anote AI 移动应用是使用 [Expo](https://expo.dev) 和 React Native 构建的。

## 功能

- 原生 iOS 和 Android 支持
- 明亮/黑暗模式（遵循系统偏好设置）
- 带有流式响应的聊天界面
- 带有滑入侧边栏的会话历史
- 通过 `expo-secure-store` 安全存储 JWT

## 本地运行

```bash
cd packages/mobile
npm install
npx expo start
```

使用 Expo Go 应用扫描二维码或在模拟器中运行。

## 配置

通过环境变量设置 API URL：

```bash
EXPO_PUBLIC_API_URL=https://api.anote.ai npx expo start
```
