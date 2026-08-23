# Aperçu de l'application mobile

L'application mobile Anote AI est construite avec [Expo](https://expo.dev) et React Native.

## Fonctionnalités

- Support natif iOS et Android
- Mode clair/sombre (suit la préférence du système)
- Interface de chat avec réponses en streaming
- Historique des sessions avec barre latérale coulissante
- Stockage sécurisé JWT via `expo-secure-store`

## Exécution en local

```bash
cd packages/mobile
npm install
npx expo start
```

Scannez le code QR avec l'application Expo Go ou exécutez-le dans un simulateur.

## Configuration

Définissez l'URL de l'API via une variable d'environnement :

```bash
EXPO_PUBLIC_API_URL=https://api.anote.ai npx expo start
```
