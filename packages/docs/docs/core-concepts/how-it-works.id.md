# Cara Kerja Panacea

Panacea menjalankan **loop agentic**: ia membaca prompt Anda, memutuskan tools mana yang akan dipanggil, mengeksekusinya, membaca hasilnya, dan mengulanginya — melakukan streaming penalaran dan perubahannya kembali kepada Anda — sampai tugas selesai atau mencapai batas turn.

## Tools

Secara default, agent Panacea dapat memanggil:

| Tool | Tujuan |
|---|---|
| `Read` | Membaca file |
| `Write` | Membuat atau menimpa file |
| `Edit` | Membuat perubahan yang ditargetkan pada file |
| `Bash` | Menjalankan perintah shell |
| `Glob` | Menemukan file berdasarkan pola |
| `Grep` | Mencari isi file |

Beberapa perintah mempersempit daftar ini — `anote review` dan `anote diff`, misalnya, hanya mengizinkan `Read`, `Glob`, `Grep`, dan `Bash`, karena review seharusnya tidak menulis file.

## Turn dan kompaksi

Setiap pasangan panggilan tool/respons dihitung sebagai satu turn. Agent berhenti setelah `maxTurns` (default 30, dapat dikonfigurasi via `anote config set maxTurns <n>` atau `.anote.json`). Sesi panjang akan dikompaksi setelah `compactAfterMessages` (default 40) agar context window tetap terkelola.

## Streaming

Setiap permukaan — CLI, VS Code, Web, Desktop — berkomunikasi dengan endpoint backend yang sama (`POST /api/chat/stream`), yang melakukan streaming respons model dan aktivitas tool melalui SSE saat terjadi. Anda dapat melihat pembacaan file, perubahan, dan output perintah secara langsung, bukan hanya jawaban akhir.

## Multi-provider

Loop agent tidak terikat pada satu model. `anote ask --compare` menjalankan prompt yang sama di beberapa model secara berdampingan, dan `--model` pada sebagian besar perintah menerima penyedia mana pun yang telah dikonfigurasi (`claude-sonnet-4-6`, `gpt-4.1`, `gemini-2.5-pro`, atau `ollama/<model>` lokal).

## Langkah selanjutnya

- [Mode Izin](../use-panacea/permission-modes.md) — kendalikan apakah agent bertanya sebelum mengedit file atau menjalankan perintah
- [Memperluas Panacea](extend.md) — CLAW.md dan hooks
- [Perintah CLI](../cli/commands.md) — referensi perintah lengkap
