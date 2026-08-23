# Ikhtisar Aplikasi Web

Aplikasi web Anote AI adalah antarmuka obrolan gaya ChatGPT yang terhubung ke backend Anote.

## Fitur

- Mode terang dan gelap (secara otomatis mendeteksi preferensi sistem)
- Respons streaming melalui SSE
- Riwayat sesi obrolan di sidebar yang dapat dilipat
- Pemilih model (Claude, GPT-4o, dll.)
- Unggah dokumen dan Tanya Jawab
- Desain responsif

## Menjalankan Secara Lokal

```bash
cd packages/web
npm install
npm run dev
```

Aplikasi berjalan di `http://localhost:3000` dan memproxy panggilan API ke `http://localhost:5000`.
