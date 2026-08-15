# Memperluas Panacea

Dua cara untuk menyesuaikan perilaku Panacea di proyek Anda: **CLAW.md** untuk instruksi persisten, dan **hooks** untuk menjalankan perintah Anda sendiri di sekitar pemanggilan tool.

## CLAW.md — memori proyek

`CLAW.md` adalah file markdown yang dibaca Panacea untuk konteks proyek — ide yang sama seperti README, tetapi ditujukan untuk agent, bukan manusia. `anote init` menghasilkannya secara otomatis, sudah terisi dengan stack yang terdeteksi dan perintah verifikasi (test/lint/build):

```markdown
# CLAW.md

This file provides guidance to Anote AI when working with code in this repository.

## Project overview

<!-- Describe what this project does -->

## Stack

TypeScript · Next.js

## Verification

Run these before considering a change complete:

  npm test
  npm run lint

## Working agreement

- Read relevant files before making changes
- Run the verification commands after modifying logic
- Keep changes small and focused
- Prefer editing existing files over creating new ones
```

Edit dengan bebas — tambahkan catatan arsitektur, konvensi, atau hal-hal yang terus-menerus salah dilakukan oleh agent. Panacea membacanya di awal setiap sesi di direktori tersebut.

## Hooks — menjalankan perintah Anda sendiri di sekitar pemanggilan tool

Hooks menjalankan perintah shell sebelum (`preToolUse`) atau sesudah (`postToolUse`) setiap pemanggilan tool, dikonfigurasi di `.anote.json`:

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
| `2` | Tolak — stdout ditangkap sebagai alasan, ditampilkan ke agent |
| lainnya | Peringatkan tapi tetap izinkan |

Gunakan `preToolUse` untuk memblokir perintah berisiko atau menerapkan kebijakan sebelum dijalankan; gunakan `postToolUse` untuk hal-hal seperti auto-format setelah setiap edit.

## Langkah selanjutnya

- [Menjelajahi direktori .anote](anote-directory.md) — di mana CLAW.md dan konfigurasi berada
- [Mode Izin](../use-panacea/permission-modes.md) — tuas lain untuk mengontrol apa yang bisa dilakukan agent
