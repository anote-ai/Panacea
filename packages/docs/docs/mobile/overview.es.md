# Descripción General de la Aplicación Móvil

La aplicación móvil de Anote AI está construida con [Expo](https://expo.dev) y React Native.

## Características

- Soporte nativo para iOS y Android
- Modo claro/oscuro (sigue la preferencia del sistema)
- Interfaz de chat con respuestas en streaming
- Historial de sesiones con barra lateral deslizante
- Almacenamiento seguro de JWT a través de `expo-secure-store`

## Ejecución Local

```bash
cd packages/mobile
npm install
npx expo start
```

Escanea el código QR con la aplicación Expo Go o ejecútalo en un simulador.

## Configuración

Establece la URL de la API a través de una variable de entorno:

```bash
EXPO_PUBLIC_API_URL=https://api.anote.ai npx expo start
```
