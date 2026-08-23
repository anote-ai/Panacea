# Visão Geral do Aplicativo Móvel

O aplicativo móvel Anote AI é construído com [Expo](https://expo.dev) e React Native.

## Recursos

- Suporte nativo para iOS e Android
- Modo claro/escuro (segue a preferência do sistema)
- Interface de chat com respostas em streaming
- Histórico de sessões com barra lateral deslizante
- Armazenamento seguro de JWT via `expo-secure-store`

## Execução Local

```bash
cd packages/mobile
npm install
npx expo start
```

Escaneie o código QR com o aplicativo Expo Go ou execute em um simulador.

## Configuração

Defina a URL da API via variável de ambiente:

```bash
EXPO_PUBLIC_API_URL=https://api.anote.ai npx expo start
```
