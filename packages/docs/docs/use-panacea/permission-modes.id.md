# Mode Izin

Panacea memiliki tiga mode izin, yang mengontrol apakah agen meminta izin sebelum menulis file atau menjalankan perintah.

| Mode | Perilaku |
|---|---|
| `default` | Mengonfirmasi sebelum mengedit file atau menjalankan perintah yang tidak hanya baca |
| `acceptEdits` | Menerima edit file secara otomatis tanpa bertanya |
| `bypassPermissions` | Menjalankan semuanya tanpa konfirmasi — gunakan dengan hati-hati |

Atur secara global atau per-proyek:

```bash
anote config set permissionMode acceptEdits
```

atau di `.anote.json`:

```json
{ "permissionMode": "acceptEdits" }
```

## Penggantian per-perintah

Sebagian besar perintah tidak memerlukan Anda untuk mengubah konfigurasi global — mereka mengambil flag mereka sendiri untuk ide yang sama:

| Flag | Tersedia di | Efek |
|---|---|---|
| `--auto` | `fix`, `refactor` | Menerima edit secara otomatis hanya untuk run ini |
| `--dry-run` | `fix`, `docs`, `migrate`, `security`, `perf`, `refactor`, `generate`, `changelog`, `commit`, `review` | Menunjukkan apa yang akan terjadi tanpa menulis apa pun |
| `--no-edit` | `ask` | Hanya baca — agen tidak dapat memodifikasi file bahkan jika ingin |
| `--yes` | `init` | Lewati prompt interaktif, terima default |

`anote fix --loop` secara otomatis mengimplikasikan `acceptEdits`, karena perlu terus mengedit di seluruh iterasi tanpa berhenti untuk bertanya setiap kali.

## Hooks sebagai lapisan kebijakan

Untuk sesuatu yang lebih spesifik daripada "tanya vs. tidak tanya" — seperti memblokir panggilan `Bash` yang menyentuh jalur tertentu — gunakan hook `preToolUse` sebagai gantinya. Lihat [Perluas Panacea](../core-concepts/extend.md).

## Langkah selanjutnya

- [Bagaimana Panacea bekerja](../core-concepts/how-it-works.md) — loop agen yang dikendalikan oleh mode ini
- [Jelajahi direktori .anote](../core-concepts/anote-directory.md) — di mana `permissionMode` berada dalam konfigurasi
