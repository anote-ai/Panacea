# Penagihan Panacea, Kunci API & Pengukuran Kredit

Resep ini menjelaskan bagaimana Panacea mengukur penggunaan, mengautentikasi pemanggil API, dan mengubah langganan Stripe menjadi saldo kredit yang dapat digunakan.

## Apa yang akan Anda pelajari

- Tiga cara permintaan dapat mengautentikasi: JWT, token sesi, atau kunci API jangka panjang
- Bagaimana kredit diperiksa dan dikurangkan per permintaan, dan bagaimana penggunaan dicatat
- Bagaimana alur checkout langganan Stripe mengalir ke saldo kredit yang diperbarui
- Bagaimana pengguna menghasilkan, mencantumkan, dan mencabut kunci API mereka sendiri
- Pengaman penyalahgunaan yang mengatur langganan baru/yang diubah

## Mengapa ini penting

Panacea bukan hanya demo RAG — ini adalah produk terukur dengan tingkat langganan yang nyata. Setiap unggahan dokumen, penyelesaian obrolan, atau panggilan evaluasi menghabiskan kredit, dan kredit diisi ulang oleh langganan Stripe yang aktif. Resep ini menjelaskan seluruh siklus: bagaimana pemanggil membuktikan siapa mereka, bagaimana identitas itu dihargai, dan bagaimana uang (melalui Stripe) berubah kembali menjadi kredit yang dapat digunakan.

## File Kunci Panacea

| File | Mengapa itu penting |
|---|---|
| `Panacea/backend/database/db_auth.py` | `extractUserEmailFromRequest()` mencoba JWT → token sesi → kunci API secara berurutan; `user_has_credits()`, `api_key_user_has_credits()`, `deduct_credits_from_api_key_user()`; pengaman penyalahgunaan di `verifyAuthForNewSubscriptipns()` |
| `Panacea/backend/database/usage.py` | `log_api_usage()` menulis satu baris per permintaan ke `api_usage`; `get_usage_summary()` / `get_usage_rows()` mendukung pelaporan penggunaan |
| `Panacea/backend/api_endpoints/payments/handler.py` | `CreateCheckoutSessionHandler`, `CreatePortalSessionHandler`, `StripeWebhookHandler` |
| `Panacea/backend/api_endpoints/generate_api_key/handler.py`, `get_api_keys/handler.py`, `delete_api_key/handler.py`, `refresh_credits/handler.py` | Mencetak, mencantumkan, mencabut kunci API; menyegarkan kredit secara manual |
| `Panacea/backend/stripe_config/portal_config.py` | Konfigurasi Portal Penagihan Stripe per tingkat |

## Cara kerjanya

1. **Autentikasi.** Setiap rute yang dilindungi memanggil `extractUserEmailFromRequest(request)`, yang membaca header `Authorization: Bearer <token>` dan mencoba, dalam urutan: mendekode sebagai JWT, mencari sebagai token sesi (`user_email_for_session_token`), kemudian mencari sebagai kunci API (`user_email_for_api_key`). Yang berhasil pertama kali menyelesaikan email pemanggil.
2. **Periksa kredit.** Sebelum melayani permintaan, backend memanggil `user_has_credits(user_email)` (pemanggil JWT/sesi) atau `api_key_user_has_credits(api_key)` (pemanggil kunci API) untuk mengonfirmasi kolom `credits` pengguna di `users` setidaknya 1.
3. **Kurangi dan catat.** Setelah selesai, `deduct_credits_from_api_key_user()` mengurangi saldo dan `log_api_usage()` menyisipkan satu baris ke dalam `api_usage` dengan endpoint, model, jumlah token, dan kredit yang dihabiskan — ini yang mendukung `GET /v1/usage` dan `GET /v1/account`.
4. **Upgrade melalui Stripe.** Frontend memanggil `POST /createCheckoutSession`, yang mengarah ke `CreateCheckoutSessionHandler`: ia menyelesaikan pengguna, memetakan `product_hash` yang diminta ke ID harga Stripe, dan membuat `stripe.checkout.Session` dalam mode `subscription` (opsional menerapkan kode percobaan gratis 30 hari).
5. **Webhook menyelesaikan siklus.** Stripe memanggil kembali `POST /stripeWebhook` pada `checkout.session.completed`; `StripeWebhookHandler` mencatat langganan baru melalui `add_subscription()` dan memanggil `refresh_credits(user_email)` untuk mengisi ulang saldo pengguna. Peristiwa `customer.subscription.updated` (pembatalan) dan `.deleted` ditangani secara simetris.
6. **Kelola langganan.** `POST /createPortalSession` (`CreatePortalSessionHandler`) membuka sesi Portal Penagihan Stripe yang dibatasi pada tingkat pengguna saat ini melalui `config_for_payment_tiers()`, sehingga peningkatan/penurunan/pembatalan terjadi melalui UI yang dihosting oleh Stripe.
7. **Kunci API.** `POST /generateAPIKey` memerlukan setidaknya 1 kredit dan memanggil `generate_api_key()`; `GET /getAPIKeys` dan `POST /deleteAPIKey` mencantumkan/mencabut kunci, masing-masing dilacak dengan cap waktu `last_used` (`touch_api_key_last_used`).

### Pengaman penyalahgunaan

`verifyAuthForNewSubscriptipns()` di `db_auth.py` membatasi langganan baru per tingkat per hari (misalnya 25/hari untuk Premium, 5/hari untuk Enterprise), mengirimkan peringatan internal melalui email pada ambang batas yang ditentukan (5, 10, 50, 100, 200, 500 langganan baru/hari), dan memblokir pengguna dari mengubah rencana lebih dari sekali dalam sebulan yang bergulir.

## Jalankan secara lokal

Dari root workspace (`anote/panacea`):

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

Atur ini di `backend/.env` untuk menjalankan alur penagihan:

```bash
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
FRONTEND_URL=http://localhost:3000
JWT_SECRET_KEY=some-dev-secret
```

Arahkan webhook Stripe ke backend lokal Anda dengan Stripe CLI:

```bash
stripe listen --forward-to localhost:5000/stripeWebhook
```

### Coba

```bash
# Menghasilkan kunci API (memerlukan JWT/sesi yang terautentikasi, dan >=1 kredit)
curl -X POST http://localhost:5000/generateAPIKey \
  -H "Authorization: Bearer <jwt_or_session_token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "my first key"}'

# Periksa penggunaan dengan kunci API baru
curl http://localhost:5000/v1/usage \
  -H "Authorization: Bearer <api_key>"
```

## Catatan untuk buku masak

Pasangkan ini dengan resep 07 (Gerbang API yang Kompatibel dengan OpenAI) — kunci API yang sama yang dihasilkan di sini adalah yang mengautentikasi panggilan `AnoteOpenAI`. Perlu dicatat kesalahan ketik `verifyAuthForNewSubscriptipns` dalam nama fungsi sebagai keanehan yang diketahui jika pembaca mencarinya di kode.
