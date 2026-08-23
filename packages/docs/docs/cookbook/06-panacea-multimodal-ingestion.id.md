# Panacea Multi-Modal Document Ingestion

Resep ini menjelaskan bagaimana Panacea memperluas Q&A dokumen + RAG (lihat [resep 03](03-panacea-document-qa-rag.md)) di luar teks biasa ke gambar, audio, video, dan spreadsheet — menjadikannya semua dapat dicari melalui pipeline chunking dan embedding yang sama.

## Apa yang akan Anda pelajari

- Bagaimana Panacea mengklasifikasikan unggahan berdasarkan tipe MIME dan mengarahkannya ke layanan pengambilan yang didedikasikan
- Bagaimana gambar dan frame video diubah menjadi teks yang dapat diindeks menggunakan LLM yang mampu melihat
- Bagaimana audio (termasuk trek audio dari video) ditranskripsi dengan Whisper
- Bagaimana spreadsheet diubah menjadi tabel Markdown alih-alih diratakan menjadi dump teks yang tidak dapat dicari
- Fitur-fitur dan batas ukuran yang mengatur pengambilan multi-modal

## Mengapa ini penting

Tika (ekstraktor teks dokumen default) hanya dapat menangani format berbasis teks dengan berguna. Tanpa penanganan tambahan, gambar, klip audio, video, atau spreadsheet yang diunggah akan gagal untuk diambil atau kehilangan semua strukturnya. Sebaliknya, Panacea mendeteksi tipe media saat waktu unggah dan memanggil layanan yang dibangun khusus yang menghasilkan teks bersih, yang kemudian disimpan sebagai `document_text` dan mengalir melalui jalur pengambilan yang sama persis seperti dokumen lainnya — sehingga tangkapan layar, rekaman panggilan, atau spreadsheet penjualan semua dapat dijawab melalui chat seperti PDF.

## File-file Kunci Panacea

| File | Mengapa ini penting |
|---|---|
| `Panacea/backend/api_endpoints/documents/handler.py` | Mendeteksi tipe MIME/ekstensi saat unggah dan mengarahkannya ke layanan pengambilan yang tepat |
| `Panacea/backend/services/vision_service.py` | `describe_image()` — menghasilkan deskripsi teks yang rinci dari gambar menggunakan GPT-4o atau Claude vision |
| `Panacea/backend/services/audio_service.py` | `transcribe_audio()` — mentranskripsi audio dengan OpenAI Whisper |
| `Panacea/backend/services/video_service.py` | Mengekstrak frame dengan `ffmpeg`, mendeskripsikan masing-masing dengan layanan visi, mentranskripsi trek audio, dan menginterleave keduanya |
| `Panacea/backend/services/tabular_service.py` | `ingest_tabular()` — mengonversi CSV/TSV/XLSX/XLS/ODS menjadi tabel Markdown yang mempertahankan header dan baris |
| `Panacea/backend/agents/config.py` | Fitur konfigurasi `AgentConfig`: `ENABLE_MULTIMODAL`, `MAX_IMAGE_BYTES`, `MAX_AUDIO_BYTES`, `MAX_VIDEO_BYTES`, `VIDEO_FRAME_INTERVAL_SECS`, `VIDEO_MAX_FRAMES` |

## Cara kerjanya

1. Sebuah file diunggah melalui endpoint yang sama yang digunakan untuk dokumen biasa; `handler.py` mendeteksi tipe MIME/ekstensi untuk mengklasifikasikannya sebagai gambar, video, audio, tabular, atau teks/dokumen biasa.
2. **Gambar** → `vision_service.describe_image()` mengirimkan gambar (dalam format base64) ke model yang mampu melihat dengan prompt yang menginstruksikannya untuk mentranskripsi teks yang terlihat, mendeskripsikan grafik/diagram/tangkapan layar UI, dan mencatat objek serta tata letak — sehingga deskripsi saja sudah cukup untuk pencarian semantik menemukannya nanti.
3. **Audio** → `audio_service.transcribe_audio()` memanggil Whisper (`whisper-1`) dan mengembalikan transkrip dengan metadata durasi/bahasa.
4. **Video** → `video_service` mengekstrak frame pada interval tetap (`VIDEO_FRAME_INTERVAL_SECS`, default 30s, dibatasi pada `VIDEO_MAX_FRAMES`) menggunakan `ffmpeg`, mendeskripsikan setiap frame dengan layanan visi, mentranskripsi trek audio secara terpisah, dan menginterleave keduanya ke dalam satu dokumen bertanda waktu.
5. **Tabular** → `tabular_service.ingest_tabular()` mem-parsing setiap sheet secara native (melalui `csv`/`pandas`+`openpyxl`/`xlrd`) dan merendernya sebagai tabel Markdown, kembali ke CSV biasa untuk baris di luar 500 pertama sehingga tidak ada yang hilang dari indeks pencarian meskipun tidak dirender dengan baik.
6. Teks apa pun yang dihasilkan dari layanan ini disimpan sebagai `document_text` dan di-chunk/embedded persis seperti dokumen normal, sehingga dapat diambil melalui alur RAG Q&A standar dari resep 03.

Setiap layanan dirancang untuk **tidak pernah mengeluarkan** — panggilan visi yang gagal, ketergantungan yang hilang, atau file yang terlalu besar mengembalikan string placeholder (misalnya `"[Gambar terlalu besar untuk analisis inline (23.4 MB). Batas: 20 MB.]"`) sehingga catatan dokumen selalu dibuat alih-alih gagal pada seluruh unggahan.

## Jalankan secara lokal

Dari root workspace (`anote/panacea`):

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

Pengambilan multi-modal diaktifkan secara default (`ENABLE_MULTIMODAL=true`). Atur ini di `backend/.env` untuk menyesuaikan perilaku:

```bash
ENABLE_MULTIMODAL=true        # saklar utama
MAX_IMAGE_BYTES=20971520      # default 20 MB
MAX_AUDIO_BYTES=26214400      # default 25 MB
MAX_VIDEO_BYTES=524288000     # default 500 MB
VIDEO_FRAME_INTERVAL_SECS=30
VIDEO_MAX_FRAMES=20
```

Pengambilan video juga memerlukan `ffmpeg` untuk ada di `PATH` kontainer backend (sudah termasuk dalam gambar Docker yang disediakan). Pengambilan Excel memerlukan `openpyxl` (XLSX/ODS) dan `xlrd` (XLS lama), dan kedua layanan visi/audio memerlukan `OPENAI_API_KEY` dan/atau `ANTHROPIC_API_KEY` yang diatur tergantung pada `DEFAULT_AGENT_MODEL_TYPE`.

### Coba ini

```bash
curl -X POST http://localhost:5000/ingest-pdf \
  -F chat_id=1 \
  -F "files[]=@./screenshot.png"

curl -X POST http://localhost:5000/ingest-pdf \
  -F chat_id=1 \
  -F "files[]=@./quarterly_sales.xlsx"
```

Kemudian, di UI web di `http://localhost:3000`, buka sesi chat yang sama dan ajukan pertanyaan tentang gambar atau spreadsheet yang baru saja Anda unggah — Panacea menjawab dari deskripsi/tabel Markdown yang dihasilkan persis seperti yang dilakukan dari PDF.

## Catatan untuk buku masak

Resep ini cocok dengan resep 03: ini adalah pipeline RAG yang sama, hanya dengan corong format input yang lebih luas. Perlu dicatat kepada pembaca bahwa "kualitas indeks" untuk gambar/video hanya sebaik deskripsi model visi, jadi penyesuaian prompt di `_INDEXING_PROMPT` `vision_service.py` adalah titik kustomisasi yang alami.
