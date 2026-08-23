# Panoramica dell'App Mobile

L'app mobile Anote AI è costruita con [Expo](https://expo.dev) e React Native.

## Caratteristiche

- Supporto nativo per iOS e Android
- Modalità chiara/scura (segue le preferenze di sistema)
- Interfaccia chat con risposte in streaming
- Cronologia delle sessioni con barra laterale a comparsa
- Archiviazione sicura dei JWT tramite `expo-secure-store`

## Esecuzione Locale

```bash
cd packages/mobile
npm install
npx expo start
```

Scansiona il codice QR con l'app Expo Go o esegui in un simulatore.

## Configurazione

Imposta l'URL dell'API tramite variabile d'ambiente:

```bash
EXPO_PUBLIC_API_URL=https://api.anote.ai npx expo start
```
