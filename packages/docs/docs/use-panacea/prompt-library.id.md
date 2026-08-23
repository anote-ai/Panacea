# Perpustakaan Prompt

Salin-tempel prompt untuk `anote ask`, `anote chat`, dan `anote fix`, yang diorganisir berdasarkan tugas.

## Memahami kode

```bash
anote ask "apa yang dilakukan kode ini, secara umum?"
anote ask --file src/payments/webhook.ts "jelaskan file ini baris demi baris"
anote ask "di mana pengatur batas laju dikonfigurasi, dan apa batasnya?"
anote ask "apa yang akan rusak jika saya menghapus lapisan caching di sini?"
```

## Debugging

```bash
anote fix --error "$(cat error.log)"
anote ask "mengapa tes ini gagal secara sporadis tetapi tidak konsisten?"
anote fix src/db/pool.ts "koneksi tidak dikembalikan ke pool"
```

## Tinjauan kode

```bash
anote review --file src/auth/session.ts
anote review --pr 42
anote diff --staged -c "fokus pada penanganan kesalahan dan kasus tepi"
```

## Refactoring

```bash
anote refactor src/utils.ts "pisahkan ini menjadi fungsi yang lebih kecil dan bertujuan tunggal" --dry-run
anote ask "apakah ada cara yang lebih sederhana untuk mengekspresikan logika ini?" --file src/parser.ts
anote migrate --from "moment" --to "date-fns"
```

## Menulis tes

```bash
anote test src/utils/validate.ts --coverage --write
anote ask "kasus tepi apa yang saya lewatkan untuk fungsi ini?" --file src/utils/validate.ts
```

## Keamanan dan kinerja

```bash
anote security --severity high
anote perf --focus "database,bundle size"
```

## Dokumentasi

```bash
anote docs src/api/client.ts --style jsdoc
anote changelog --since v1.2.0
anote explain --stdout                       # ringkasan arsitektur cepat
```

## Langkah selanjutnya

- [Alur kerja umum](common-workflows.md)
- [Perintah CLI](../cli/commands.md)
