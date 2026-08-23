# Jelajahi Direktori .anote

CLI Panacea membaca konfigurasi dari dua tempat: file per-proyek dan satu global.

## Konfigurasi proyek

Panacea mencari ke atas dari direktori saat ini untuk file pertama yang ditemukan, dalam urutan ini:

- `.anote.json`
- `.claw.json`
- `anote.config.json`

```json
{
  "model": "claude-sonnet-4-6",
  "permissionMode": "default",
  "maxTurns": 20,
  "compactAfterMessages": 40,
  "hooks": {
    "preToolUse": [],
    "postToolUse": []
  }
}
```

| Kunci | Tujuan |
|---|---|
| `model` | Model default untuk proyek ini |
| `permissionMode` | `default`, `acceptEdits`, atau `bypassPermissions` — lihat [Mode izin](../use-panacea/permission-modes.md) |
| `provider` | Override penyedia eksplisit (biasanya terdeteksi otomatis dari `model`) |
| `baseUrl` | URL dasar untuk endpoint yang kompatibel dengan OpenAI, misalnya `http://localhost:11434/v1` untuk Ollama |
| `maxTurns` | Batas giliran per sesi |
| `compactAfterMessages` | Kapan untuk mengompak riwayat sesi |
| `hooks` | Hook shell `preToolUse` / `postToolUse` — lihat [Perluas Panacea](extend.md) |

`anote init` membuat `.anote.json` untuk Anda. `anote config` membacanya dan menulisnya:

```bash
anote config              # tampilkan konfigurasi yang berlaku (global + lokal)
anote config get model
anote config set model gpt-4.1
anote config path         # cetak jalur file konfigurasi global
anote config edit         # buka konfigurasi global di $EDITOR
```

## Konfigurasi global

`~/.anote/config.json` menyimpan default Anda — diterapkan kapan pun proyek tidak menimpanya. Konfigurasi proyek selalu lebih diutamakan daripada konfigurasi global.

## CLAW.md

Bukan JSON — file markdown yang dibaca agen untuk konteks proyek di awal setiap sesi. Lihat [Perluas Panacea](extend.md) untuk apa yang dimasukkan ke dalamnya.

## Langkah selanjutnya

- [Mode izin](../use-panacea/permission-modes.md)
- [Kelola sesi](../use-panacea/sessions.md)
