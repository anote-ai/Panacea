# Panacea AI Coding Toolchain

Resep ini menjelaskan bagaimana pengalaman pengkodean AI Panacea disampaikan melalui CLI, SDK, dan VS Code.

## Apa yang akan Anda pelajari

- Berbagai titik masuk pengkodean AI di Panacea
- Bagaimana CLI, SDK, dan ekstensi VS Code terkait dengan backend yang sama
- Kemampuan produk utama untuk bantuan kode pribadi
- Di mana mencari detail implementasi di repositori

## Mengapa ini penting

Panacea dibangun sebagai produk terpadu dengan beberapa antarmuka:

- sebuah **CLI** yang menggerakkan `anote chat`, pencarian kode, dan tinjauan repositori
- sebuah **ekstensi VS Code** untuk bantuan AI di dalam editor
- sebuah **SDK** untuk menyematkan Panacea ke dalam aplikasi lain

Antarmuka ini berbagi backend dan lapisan penalaran yang didorong oleh agen, yang membuat produk konsisten di desktop, web, dan alur kerja kode.

## File-file Kunci Panacea

| File | Mengapa ini penting |
|---|---|
| `Panacea/packages/cli` | Implementasi CLI TypeScript untuk alur kerja pengembang |
| `Panacea/packages/vscode` | Ekstensi VS Code dan integrasi chat |
| `Panacea/packages/sdk` | SDK TypeScript untuk akses programatik |
| `Panacea/packages/backend` | Layanan backend bersama yang mendukung semua interaksi UI dan CLI |

## Cara kerjanya

- Tindakan pengguna pengkodean dimulai di CLI, SDK, atau ekstensi VS Code.
- Permintaan dikirim ke API backend Panacea.
- Backend menggunakan orkestrasi agen dan penyedia model untuk menghasilkan jawaban yang memahami kode.
- Respons dikembalikan di antarmuka yang sama, dengan saran kode, penjelasan, atau perbaikan.

## Fitur produk yang berguna

- **CLI**: `anote chat`, pencarian repositori, tinjauan kode, generasi kode, dan bantuan yang didorong oleh embeddings.
- **VS Code**: chat inline, pratinjau diff, tindakan kode, dan respons streaming.
- **SDK**: pembungkus klien untuk API Panacea, memungkinkan integrasi kustom.

## Jalankan secara lokal

Dari root workspace (`anote/panacea`):

```bash
cd Panacea
cp packages/backend/.env.example packages/backend/.env
docker compose up --build
```

Ini memulai layanan backend dan frontend bersama.

Di terminal lain, jalankan paket CLI:

```bash
cd Panacea/packages/cli
npm install
npm run dev
```

Kemudian Anda dapat menggunakan CLI secara lokal atau membangunnya dengan `npm run build`.

Untuk pengembangan VS Code, buka `Panacea/packages/vscode` di VS Code dan luncurkan ekstensi dengan debugger.

## Catatan untuk buku masak

Resep ini berguna bagi rekan tim yang membutuhkan panduan tingkat tinggi tentang produk pengkodean AI multi-antarmuka Panacea. Ini juga dapat mengarahkan pembaca ke file implementasi yang dapat mereka modifikasi atau perluas.
