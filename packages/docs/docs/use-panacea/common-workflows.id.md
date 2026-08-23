# Alur Kerja Umum

Polanya langkah-demi-langkah untuk tugas sehari-hari dengan CLI Panacea.

## Jelajahi kode basis yang tidak dikenal

```bash
anote explain                       # menghasilkan tur CODEBASE.md
anote explain src/auth.ts "bagaimana ini bekerja?"
anote index && anote search "validasi JWT"
```

`explain` tanpa argumen menulis gambaran `CODEBASE.md` dari seluruh repositori. Arahkan ke file atau ajukan pertanyaan spesifik untuk mendalami lebih jauh.

## Perbaiki bug

```bash
anote fix --error "TypeError: tidak dapat membaca properti 'id' dari undefined"
anote fix src/handler.ts "penangan webhook menjatuhkan peristiwa di bawah beban"
anote fix --loop --cmd "npm test"          # terus iterasi sampai tes lulus
```

## Tulis dan komit

```bash
anote generate "middleware pembatas laju untuk Express" -o src/middleware/rateLimit.ts
anote test src/middleware/rateLimit.ts --write
anote commit                                # pesan komit yang dihasilkan AI
```

## Tinjau sebelum Anda dorong

```bash
anote diff --staged                         # tinjau perubahan yang sudah dipentaskan
anote review --pr 42                        # atau tinjau PR GitHub yang terbuka
anote security --severity high              # audit OWASP Top 10
```

## Buka permintaan tarik

```bash
anote pr --gh                               # menghasilkan deskripsi, buka dengan CLI gh
```

## Refactor dengan aman

```bash
anote refactor src/legacy.ts "ekstrak logika validasi ke dalam fungsinya sendiri" --dry-run
anote refactor src/legacy.ts "ekstrak logika validasi ke dalam fungsinya sendiri" --auto
```

Selalu coba `--dry-run` terlebih dahulu pada apa pun yang belum Anda tinjau.

## Terus bekerja sambil melakukan hal lain

```bash
anote watch "src/**/*.ts"                   # analisis ulang pada setiap simpan
```

## Dokumentasikan saat Anda berjalan

```bash
anote docs src/api.ts --style jsdoc
anote changelog --since v1.2.0
```

## Langkah selanjutnya

- [Perpustakaan prompt](prompt-library.md) — titik awal salin-tempel
- [Perintah CLI](../cli/commands.md) — referensi lengkap untuk flag
