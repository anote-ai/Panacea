# Orkestrasi Multi-Agen Panacea

Resep ini menjelaskan arsitektur orkestrasi agen Panacea: bagaimana orkestrator menetapkan tugas, memilih agen, dan mendukung alur kerja berurutan dan hierarkis.

## Apa yang akan Anda pelajari

- Peran orkestrator sebagai otak sistem
- Bagaimana Panacea mengarahkan tugas ke agen spesialis
- Perbedaan antara alur kerja berurutan dan hierarkis
- Bagaimana kru agen berkolaborasi untuk mencapai tujuan bersama
- Bagaimana pendaftaran alat bekerja sehingga agen dapat menggunakan kemampuan baru

## Mengapa ini penting

Di Panacea, orkestrator tidak acak. Ia memilih agen terbaik berdasarkan deskripsi kemampuan, konteks tugas, dan status alur kerja. Hal ini membuat sistem dapat diprediksi dan dapat diperluas.

## Konsep kunci

- **Orkestrator** — koordinator pusat yang memutuskan agen mana yang dijalankan selanjutnya
- **Agen** — unit otonom dengan tujuan yang jelas, seperti `DocumentRetrievalAgent`, `GeneralKnowledgeAgent`, atau `ChatHistoryAgent`
- **Kru** — sekelompok agen yang bekerja sama menuju tujuan bersama
- **Alur kerja** — gaya kolaborasi; dapat berupa:
  - **Berurutan**: satu langkah mengikuti langkah lainnya secara berurutan
  - **Hierarkis**: rantai komando di mana orkestrator mendelegasikan subtugas kepada spesialis
- **Alat** — fungsi yang dapat dipanggil agen untuk melakukan tindakan seperti mencari, mengunggah, atau mengeksekusi kode

## File kunci Panacea

| File | Mengapa ini penting |
|---|---|
| `Panacea/backend/agents/multi_agent_system.py` | Logika orkestrator dan pengalihan alur kerja |
| `Panacea/backend/agents/autonomous_agent.py` | Pendaftaran alat dan siklus hidup agen |
| `Panacea/backend/agents/routing.py` | Logika pembantu pengalihan tugas |
| `Panacea/backend/agents/reactive_agent.py` | Menginisialisasi sistem multi-agen dan menghubungkannya ke alur percakapan |

## Cara kerjanya

1. Seorang pengguna mengajukan tugas atau pertanyaan.
2. Agen orkestrator meninjau input dan memilih agen berikutnya berdasarkan kemampuan dan persyaratan tugas.
3. Agen spesialis mengeksekusi bagian mereka dari jalur dan dapat mengembalikan hasil sementara.
4. Orkestrator dapat melanjutkan secara berurutan atau terus mendelegasikan subtugas dalam pola hierarkis.
5. Hasil akhir dirakit dan dikembalikan kepada pengguna.

### Alur kerja berurutan

Alur kerja berurutan berguna untuk jalur tetap seperti:

- mengambil potongan dokumen → merangkum → menjawab pengguna
- mengumpulkan konteks kode → menganalisis kode → mengembalikan saran ulasan

Setiap langkah dijalankan secara berurutan, dan langkah berikutnya menggunakan output dari langkah sebelumnya.

### Alur kerja hierarkis

Alur kerja hierarkis berguna untuk tugas kompleks di mana orkestrator mengelola spesialis:

- orkestrator menetapkan satu agen untuk mengumpulkan data
- agen lain memvalidasi data
- agen ketiga menghasilkan respons akhir

Ini mirip dengan rantai komando: orkestrator tetap mengendalikan dan mendelegasikan pekerjaan kepada agen yang ahli di bidangnya.

## Pendaftaran alat

Panacea mendukung pendaftaran alat secara dinamis. Jika seorang agen membutuhkan kemampuan baru, ia dapat memanggil `register_tool(...)` dari `backend/agents/autonomous_agent.py`.

Artinya, buku masak dapat mendokumentasikan tidak hanya cara menggunakan alat yang ada, tetapi juga cara menambahkan alat baru ke sistem.

## Umpan balik

Umpan balik pengguna sangat penting untuk meningkatkan pemilihan agen. Panacea mencatat umpan balik dari Q&A dokumen dan hasil tugas sehingga orkestrator dapat belajar agen dan alat mana yang menghasilkan hasil terbaik.

## Catatan untuk buku masak

Resep ini adalah kandidat kuat untuk penjelasan manual. Ini harus mencakup diagram atau contoh alur langkah-demi-langkah yang menunjukkan mengapa orkestrator membuat keputusan alih-alih membiarkan pemilihan agen menjadi kebetulan.
