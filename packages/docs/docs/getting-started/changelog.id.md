# Catatan Perubahan

Panacea belum menerbitkan file catatan perubahan yang dikelola secara manual — sumber kebenaran untuk apa yang telah dirilis adalah:

- **[Rilis GitHub](https://github.com/anote-ai/Panacea/releases)** — rilis yang ditandai untuk CLI, ekstensi VS Code, dan paket lainnya
- **[Riwayat komit](https://github.com/anote-ai/Panacea/commits/main)** — setiap perubahan, dalam urutan

## Buat satu untuk proyek Anda sendiri

CLI dapat menulis catatan perubahan dari riwayat git untuk *kode sumber* Anda:

```bash
anote changelog                    # sejak tag terakhir
anote changelog --since v1.2.0
anote changelog --dry-run          # cetak alih-alih menulis CHANGELOG.md
```

Ini menulis ke `CHANGELOG.md` proyek Anda sendiri, bukan milik Panacea.
