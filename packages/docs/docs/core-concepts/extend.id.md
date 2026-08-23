# Perluas Panacea

Dua cara untuk menyesuaikan bagaimana Panacea berperilaku dalam proyek Anda: **CLAW.md** untuk instruksi yang persisten, dan **hooks** untuk menjalankan perintah Anda sendiri di sekitar panggilan alat.

## CLAW.md — memori proyek

`CLAW.md` adalah file markdown yang dibaca Panacea untuk konteks proyek — ide yang sama seperti README yang ditujukan untuk agen daripada manusia. `anote init` secara otomatis menghasilkan satu, diisi sebelumnya dengan tumpukan yang terdeteksi dan perintah verifikasi (uji/lint/bangun):

```markdown
# CLAW.md

File ini memberikan panduan kepada Anote AI saat bekerja dengan kode di repositori ini.

## Gambaran proyek

<!-- Deskripsikan apa yang dilakukan proyek ini -->

## Tumpukan

TypeScript · Next.js

## Verifikasi

Jalankan ini sebelum mempertimbangkan perubahan selesai:

  npm test
  npm run lint

## Kesepakatan kerja

- Baca file yang relevan sebelum melakukan perubahan
- Jalankan perintah verifikasi setelah memodifikasi logika
- Jaga agar perubahan kecil dan terfokus
- Lebih suka mengedit file yang ada daripada membuat yang baru
```

Edit dengan bebas — tambahkan catatan arsitektur, konvensi, atau hal-hal yang terus salah dipahami oleh agen. Panacea membacanya di awal setiap sesi di direktori tersebut.

## Hooks — jalankan perintah Anda sendiri di sekitar panggilan alat

Hooks menjalankan perintah shell sebelum (`preToolUse`) atau setelah (`postToolUse`) setiap panggilan alat, yang dikonfigurasi dalam `.anote.json`:

```json
{
  "hooks": {
    "preToolUse": ["./scripts/check-tool-policy.sh"],
    "postToolUse": ["npx prettier --write ."]
  }
}
```

**Semantik kode keluar:**

| Kode keluar | Efek |
|---|---|
| `0` | Izinkan — stdout ditangkap sebagai pesan informasi |
| `2` | Tolak — stdout ditangkap sebagai alasan, ditampilkan kepada agen |
| yang lainnya | Peringatan tetapi izinkan |

Gunakan `preToolUse` untuk memblokir perintah berisiko atau menegakkan kebijakan sebelum mereka dijalankan; gunakan `postToolUse` untuk hal-hal seperti pemformatan otomatis setelah setiap edit.

## Langkah selanjutnya

- [Jelajahi direktori .anote](anote-directory.md) — tempat CLAW.md dan konfigurasi berada
- [Mode izin](../use-panacea/permission-modes.md) — tuas lain tentang apa yang dapat dilakukan agen
