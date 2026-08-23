# Ikhtisar Aplikasi Seluler

Aplikasi seluler Anote AI dibangun dengan [Expo](https://expo.dev) dan React Native.

## Fitur

- Dukungan iOS dan Android asli
- Mode terang/gelap (mengikuti preferensi sistem)
- Antarmuka obrolan dengan respons streaming
- Riwayat sesi dengan sidebar yang muncul
- Penyimpanan JWT yang aman melalui `expo-secure-store`

## Menjalankan Secara Lokal

```bash
cd packages/mobile
npm install
npx expo start
```

Pindai kode QR dengan aplikasi Expo Go atau jalankan di simulator.

## Konfigurasi

Atur URL API melalui variabel lingkungan:

```bash
EXPO_PUBLIC_API_URL=https://api.anote.ai npx expo start
```
