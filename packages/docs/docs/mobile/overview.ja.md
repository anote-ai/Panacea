# モバイルアプリの概要

Anote AI モバイルアプリは [Expo](https://expo.dev) と React Native で構築されています。

## 機能

- ネイティブ iOS および Android サポート
- ライト/ダークモード（システムの設定に従う）
- ストリーミングレスポンスを持つチャットインターフェース
- スライドインサイドバー付きのセッション履歴
- `expo-secure-store` を介した安全な JWT ストレージ

## ローカルでの実行

```bash
cd packages/mobile
npm install
npx expo start
```

Expo Go アプリで QR コードをスキャンするか、シミュレーターで実行します。

## 設定

環境変数を介して API URL を設定します：

```bash
EXPO_PUBLIC_API_URL=https://api.anote.ai npx expo start
```
