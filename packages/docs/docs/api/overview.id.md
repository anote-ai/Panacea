# Ikhtisar API Backend

Backend Anote adalah API Flask terpadu yang melayani semua antarmuka klien.

URL Dasar: `http://localhost:5000` (lokal) atau URL backend yang telah Anda deploy.

## Autentikasi

Semua endpoint yang dilindungi memerlukan token JWT:

```
Authorization: Bearer <token>
```

Dapatkan token melalui `POST /auth/login` atau `POST /auth/register`.

## Endpoint Utama

### Obrolan Agen (Streaming)

```
POST /api/chat/stream          # Obrolan streaming SSE
POST /api/chat                 # Obrolan non-streaming
GET  /api/chat/sessions        # Daftar sesi
POST /api/chat/sessions        # Buat sesi
```

### Dokumen

```
POST /api/documents/upload     # Unggah dokumen
GET  /api/documents            # Daftar dokumen
GET  /api/documents/{id}       # Dapatkan dokumen
DELETE /api/documents/{id}     # Hapus dokumen
POST /api/documents/{id}/ask   # Tanya jawab pada dokumen
```

### Pencarian Semantik

```
GET  /api/search?q=...&cwd=... # Cari basis kode yang diindeks
```

### Autentikasi

```
POST /auth/register            # Daftar
POST /auth/login               # Masuk
POST /auth/refresh             # Segarkan JWT
GET  /auth/google              # Google OAuth
```

### Pengguna & Penagihan

```
GET  /api/user/profile         # Dapatkan pengguna
POST /api/payments/checkout    # Checkout Stripe
POST /api/payments/portal      # Portal pelanggan
POST /api/payments/webhook     # Webhook Stripe
```
