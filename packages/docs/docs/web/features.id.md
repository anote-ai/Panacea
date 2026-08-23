# Fitur Aplikasi Web

## Antarmuka Obrolan

Tampilan obrolan utama mencerminkan desain ChatGPT: sidebar kiri yang dapat dilipat dengan riwayat sesi, dan utas pesan yang terpusat dengan bilah input di bagian bawah.

## Mode Terang / Gelap

Beralih dengan tombol di pojok kanan atas. Preferensi disimpan di `localStorage`.

- **Terang**: latar belakang putih/abu-abu terang, teks hitam
- **Gelap**: latar belakang `#212121`/`#2F2F2F`, teks putih

## Streaming

Input mengirim permintaan `POST /api/chat/stream` dan membaca respons SSE. Tombol berhenti membatalkan aliran di tengah.

## Sesi

Setiap percakapan adalah sesi yang disimpan di sisi server. Sesi terdaftar di sidebar dan bertahan di antara pemuatan halaman.
