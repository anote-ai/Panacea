# Panacea Dokumen Q&A + RAG

Resep ini menjelaskan bagaimana Panacea membangun pertanyaan-jawaban dokumen pribadi dengan generasi yang ditingkatkan dengan pengambilan (RAG).

## Apa yang akan Anda pelajari

- Bagaimana Panacea mengimpor dokumen dan menyimpannya sebagai teks yang dapat dicari
- Bagaimana backend mengambil potongan relevan untuk sebuah pertanyaan
- Bagaimana sistem menggunakan embedding dan sumber dokumen untuk mendasari jawaban
- Bagaimana umpan balik Q&A ditangkap dan meningkatkan respons di masa depan

## Mengapa ini penting

Panacea dirancang untuk memungkinkan tim mengajukan pertanyaan tentang dokumen pribadi tanpa mengirimkannya ke layanan obrolan pihak ketiga. Alur kerja adalah:

1. Unggah dokumen
2. Pecah dan sematkan konten
3. Ambil potongan relevan untuk kueri pengguna
4. Jawab menggunakan LLM dengan kutipan
5. Tangkap umpan balik untuk meningkatkan kualitas

## File Kunci Panacea

| File | Mengapa ini penting |
|---|---|
| `Panacea/backend/api_endpoints/documents/handler.py` | Rute API untuk unggah dan pengimporan dokumen |
| `Panacea/backend/database/db.py` | Logika SQL untuk penyimpanan dan pengambilan dokumen |
| `Panacea/backend/database/qa_feedback.py` | Penangkapan umpan balik untuk Q&A dokumen |
| `Panacea/backend/agents/multi_agent_system.py` | Agen pengambilan dokumen yang digunakan dalam alur kerja multi-agen |

## Cara kerjanya

- Dokumen diunggah melalui backend dan disimpan di `documents.document_text`.
- Sistem memecah dokumen besar dan membuat metadata pengambilan untuk pencarian cepat.
- Ketika pengguna mengajukan pertanyaan, Panacea memilih satu atau lebih agen khusus untuk mengambil potongan terbaik dan kemudian menghasilkan jawaban.
- Hasilnya mencakup kutipan sumber sehingga pengguna dapat melacak jawaban kembali ke dokumen asli.
- Sinyal umpan balik dicatat di `qa_feedback` untuk memungkinkan perbaikan kualitas di masa depan.

## Jalankan secara lokal

Dari root workspace (`anote/panacea`):

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

Ini memulai backend, aplikasi web, MySQL, Redis, dan Tika.

Jika Anda sudah berada di dalam folder resep, gunakan:

```bash
cd ../../../Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

Buka `http://localhost:3000` untuk menggunakan antarmuka web Panacea. Unggahan dokumen ditangani oleh rute backend `POST /ingest-pdf` dengan field formulir yang diperlukan `chat_id` dan `files[]`.

Contoh perintah unggah:

```bash
curl -X POST http://localhost:5000/ingest-pdf \
  -F chat_id=1 \
  -F "files[]=@./path/to/document.pdf"
```

### Panduan unggah minimal

1. Mulai Panacea dari root repo:

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

2. Di terminal lain, unggah satu dokumen teks atau PDF:

```bash
curl -X POST http://localhost:5000/ingest-pdf \
  -F chat_id=1 \
  -F "files[]=@./Cookbook/recipes/03-panacea-document-qa-rag/data/sample-doc.txt"
```

3. Konfirmasi bahwa backend mengembalikan respons `Dokumen Diunggah` yang berhasil.

4. Gunakan antarmuka web di `http://localhost:3000` dan pilih sesi obrolan yang sama untuk mengajukan pertanyaan tentang dokumen yang diunggah.

Jika Anda ingin menguji API secara langsung setelah unggah, temukan ID sesi obrolan di UI atau database dan kirim pertanyaan melalui alur obrolan aplikasi. Panacea akan mengambil potongan relevan dan menghasilkan jawaban yang mendasar.

## Catatan untuk buku masak

Resep ini ideal untuk entri buku masak yang menjelaskan bagaimana Panacea mendukung pekerjaan pengetahuan pribadi. Ini lebih konseptual daripada skrip satu baris, karena nilai sebenarnya adalah memahami arsitektur pengimporan dan pengambilan dokumen.
