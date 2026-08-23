# Mobile App Übersicht

Die Anote AI mobile App ist mit [Expo](https://expo.dev) und React Native erstellt.

## Funktionen

- Native Unterstützung für iOS und Android
- Hell-/Dunkelmodus (folgt der Systemeinstellung)
- Chat-Oberfläche mit Streaming-Antworten
- Sitzungsverlauf mit einblendbarer Seitenleiste
- Sichere JWT-Speicherung über `expo-secure-store`

## Lokal Ausführen

```bash
cd packages/mobile
npm install
npx expo start
```

Scannen Sie den QR-Code mit der Expo Go App oder führen Sie es in einem Simulator aus.

## Konfiguration

Setzen Sie die API-URL über eine Umgebungsvariable:

```bash
EXPO_PUBLIC_API_URL=https://api.anote.ai npx expo start
```
