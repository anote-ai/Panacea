# Mobile App Overview

The Anote AI mobile app is built with [Expo](https://expo.dev) and React Native.

## Features

- Native iOS and Android support
- Light/dark mode (follows system preference)
- Chat interface with streaming responses
- Session history with slide-in sidebar
- Secure JWT storage via `expo-secure-store`

## Running Locally

The mobile app isn't published to an app store yet — running it locally via Expo is currently the only way to use it.

1. Install dependencies and start the dev server:

   ```bash
   cd packages/mobile
   npm install
   npx expo start
   ```

2. Scan the QR code with the [Expo Go](https://expo.dev/go) app on your phone, or press `i`/`a` in the terminal to launch an iOS/Android simulator
3. Register or log in — your session token is stored securely on-device via `expo-secure-store`
4. Chat as you would in the web app: streaming responses, session history in the slide-in sidebar, light/dark mode following your system setting

## Configuration

Set the API URL via environment variable:

```bash
EXPO_PUBLIC_API_URL=https://api.anote.ai npx expo start
```
