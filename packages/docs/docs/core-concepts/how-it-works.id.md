# Cara Kerja Panacea

Panacea menjalankan **loop agensi**: ia membaca prompt Anda, memutuskan alat mana yang akan dipanggil, mengeksekusinya, membaca hasilnya, dan mengulangi — mengalirkan penalaran dan editannya kembali kepada Anda — sampai tugas selesai atau mencapai batas giliran.

## Alat-alat

Secara default, agen Panacea dapat memanggil:

| Alat | Tujuan |
|---|---|
| `Read` | Membaca file |
| `Write` | Membuat atau menimpa file |
| `Edit` | Melakukan perubahan terarah pada file |
| `Bash` | Menjalankan perintah shell |
| `Glob` | Mencari file berdasarkan pola |
| `Grep` | Mencari konten file |

Beberapa perintah mempersempit daftar ini — `anote review` dan `anote diff`, misalnya, hanya memperbolehkan `Read`, `Glob`, `Grep`, dan `Bash`, karena sebuah review seharusnya tidak menulis file.

## Giliran dan kompaksi

Setiap pasangan panggilan/respons alat dihitung sebagai satu giliran. Agen berhenti setelah `maxTurns` (default 30, dapat dikonfigurasi melalui `anote config set maxTurns <n>` atau `.anote.json`). Sesi panjang dikompaksi setelah `compactAfterMessages` (default 40) untuk menjaga jendela konteks tetap dapat dikelola.

## Streaming

Setiap permukaan — CLI, VS Code, Web, Desktop — berbicara dengan endpoint backend yang sama (`POST /api/chat/stream`), yang mengalirkan respons model dan aktivitas alat melalui SSE saat terjadi. Anda melihat pembacaan file, editan, dan output perintah secara langsung, bukan hanya jawaban akhir.

## Multi-provider

Loop agen tidak terikat pada satu model. `anote ask --compare` menjalankan prompt yang sama di beberapa model secara berdampingan, dan `--model` pada sebagian besar perintah menerima penyedia yang telah dikonfigurasi (`claude-sonnet-4-6`, `gpt-4.1`, `gemini-2.5-pro`, atau `ollama/<model>` lokal).

## Langkah selanjutnya

- [Mode izin](../use-panacea/permission-modes.md) — mengontrol apakah agen meminta izin sebelum mengedit atau menjalankan perintah
- [Perluas Panacea](extend.md) — CLAW.md dan hooks
- [Perintah CLI](../cli/commands.md) — referensi perintah lengkap
