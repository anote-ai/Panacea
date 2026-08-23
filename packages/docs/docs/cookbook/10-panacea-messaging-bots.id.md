# Panacea Multi-Channel Messaging Bots

Resep ini menjelaskan integrasi gaya chat-ops dari Panacea: bot Slack, SMS, dan WhatsApp yang berdiri sendiri yang memungkinkan pengguna mengajukan pertanyaan pemrograman dari aplikasi pesan yang sudah mereka gunakan.

## Apa yang akan Anda pelajari

- Pola desain yang sama di ketiga bot: menerima → memanggil LLM → memangkas sesuai batas karakter saluran → membalas
- Bagaimana bot Slack menangani threading dan mengedit placeholder "thinking…" di tempat
- Bagaimana bot SMS/WhatsApp membalas secara sinkron menggunakan Twilio's TwiML
- Celah arsitektural saat ini yang perlu diketahui sebelum memperluas bot ini

## Mengapa ini penting

Tidak setiap pengguna ingin membuka UI web atau IDE untuk mengajukan pertanyaan — integrasi gaya chat-ops memenuhi orang di tempat mereka berada. Setiap bot adalah layanan Flask kecil yang dapat diterapkan secara independen, sehingga tim dapat menjalankan hanya saluran yang mereka butuhkan (misalnya, hanya Slack) tanpa harus menyiapkan sisa tumpukan Panacea.

## File Kunci Panacea

| File | Mengapa ini penting |
|---|---|
| `Panacea/packages/bots/slack/app.py` | Aplikasi Slack Bolt; mendukung Socket Mode atau HTTP webhook; placeholder "thinking…" yang terthread diperbarui di tempat |
| `Panacea/packages/bots/sms/app.py` | Penangan webhook SMS Twilio (`MessagingResponse`/TwiML) |
| `Panacea/packages/bots/whatsapp/app.py` | Penangan webhook sandbox WhatsApp Twilio |
| `Panacea/packages/bots/{slack,sms,whatsapp}/.env.example` | Kredensial yang diperlukan per saluran |

## Cara kerjanya

1. **Slack** (`slack/app.py`): mendengarkan peristiwa `app_mention`. `extract_query()` menghapus penyebutan `<@BOT_ID>` dari teks pesan. Ini segera memposting pesan placeholder `_Anote is thinking…_`, kemudian menjalankan panggilan LLM di thread latar belakang dan baik mengedit placeholder itu di tempat melalui `client.chat_update(...)` atau, jika posting placeholder gagal, mengirim balasan terthread yang baru.
2. **SMS** (`sms/app.py`): Twilio POST setiap teks masuk ke `/sms` sebagai data formulir (`Body`, `From`). Penangan memanggil LLM secara sinkron dan mengembalikan `MessagingResponse` (TwiML) dengan balasan — Twilio mengirimkannya sebagai teks lanjutan.
3. **WhatsApp** (`whatsapp/app.py`): pola TwiML yang sama seperti SMS, terhubung ke webhook sandbox WhatsApp Twilio alih-alih nomor telepon.
4. Ketiga bot memanggil **Anthropic API secara langsung** (`anthropic.Anthropic(...).messages.create(...)`) dengan prompt sistem bersama yang menggambarkan Anote sebagai asisten pemrograman — mereka saat ini tidak melalui backend Panacea sendiri, sehingga mereka tidak mendapatkan RAG/penggandaan dokumen, pengukuran kredit, atau orkestrasi multi-agen dari resep 03/04/08.
5. Balasan dipangkas sesuai batas setiap saluran sebelum dikirim: Slack 2900 karakter, SMS/WhatsApp 1600 karakter, masing-masing dengan pemberitahuan pemangkasan yang dilampirkan jika terpotong.

### Celah arsitektural yang perlu diketahui

Karena bot ini memanggil Anthropic secara langsung alih-alih melalui backend Panacea, pengguna Slack/SMS/WhatsApp saat ini tidak dapat mengajukan pertanyaan yang didasarkan pada dokumen yang telah mereka unggah ke Panacea, dan penggunaan mereka tidak diukur melalui sistem kredit di resep 08. Jika Anda ingin paritas saluran dengan UI web, langkah selanjutnya yang alami adalah mengganti panggilan langsung `anthropic_client.messages.create(...)` dengan permintaan ke `/v1/chat/completions` milik Panacea sendiri (gerbang yang kompatibel dengan OpenAI di resep 07) sehingga bot ini mewarisi RAG, orkestrasi, dan penagihan secara gratis.

## Jalankan secara lokal

Setiap bot bersifat independen — instal dan jalankan hanya yang Anda butuhkan.

### Slack

```bash
cd Panacea/packages/bots/slack
pip install -r requirements.txt
cp .env.example .env   # isi SLACK_BOT_TOKEN, SLACK_SIGNING_SECRET, ANTHROPIC_API_KEY
python app.py
```

Set `SLACK_APP_TOKEN` di `.env` untuk menjalankan dalam Socket Mode (tidak perlu URL publik); jika tidak, ia melayani HTTP di `PORT` (default 3000) dan mengharapkan webhook API Acara Slack diarahkan ke `POST /slack/events`.

### SMS

```bash
cd Panacea/packages/bots/sms
pip install -r requirements.txt
cp .env.example .env   # isi ANTHROPIC_API_KEY
python app.py
```

Konfigurasikan webhook SMS nomor telepon Twilio Anda ke `POST https://<your-host>/sms` (port default 3001).

### WhatsApp

```bash
cd Panacea/packages/bots/whatsapp
pip install -r requirements.txt
cp .env.example .env   # isi ANTHROPIC_API_KEY
python app.py
```

Konfigurasikan webhook sandbox WhatsApp Twilio Anda untuk diarahkan ke `POST /whatsapp` di layanan ini.

Setiap bot juga mengekspos `GET /health` untuk pemeriksaan liveness cepat.

## Catatan untuk buku masak

Ini adalah resep "memperluas Panacea" yang baik: pembaca dapat melihat versi langsung ke Anthropic berfungsi dalam beberapa menit, kemudian mengikuti catatan celah arsitektural di atas untuk menghubungkannya melalui backend Panacea sebagai gantinya untuk jawaban yang terukur dan terarah.
