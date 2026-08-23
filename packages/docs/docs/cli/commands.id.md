# Perintah CLI

## `anote ask`

Ajukan pertanyaan apa pun tentang kode Anda.

```bash
anote ask "bagaimana cara kerja middleware otentikasi?"
anote ask --file src/auth.ts "jelaskan file ini"
anote ask --compare  # berdampingan di beberapa model
cat file.py | anote ask "temukan bug"
```

## `anote fix`

Perbaiki bug di direktori saat ini.

```bash
anote fix
anote fix --loop                    # iterasi sampai tes berhasil
anote fix --max-iterations 5        # batasi iterasi
anote fix --file src/broken.ts      # perbaiki file tertentu
```

## `anote review`

Tinjau kode untuk bug, masalah keamanan, dan kualitas.

```bash
anote review                        # tinjau direktori saat ini
anote review --file src/handler.ts  # tinjau file tertentu
anote review --pr 42                # kirim tinjauan AI di GitHub PR
```

## `anote index`

Bangun indeks pencarian semantik TF-IDF dari basis kode Anda.

```bash
anote index              # indeks direktori saat ini
anote index --watch      # pantau perubahan dan indeks ulang
anote index /path/to/dir # indeks direktori tertentu
```

## `anote search`

Cari basis kode yang telah diindeks secara semantik.

```bash
anote search "validasi token JWT"
anote search "koneksi database" --top 10
anote search "middleware auth" --json
```

## `anote doctor`

Periksa lingkungan Anda untuk masalah konfigurasi.

```bash
anote doctor
```

Pemeriksaan: Node.js ≥ 18, `ANTHROPIC_API_KEY` disetel, `.anote.json` ada, `CLAW.md` ada, git terinstal.

## `anote changelog`

Hasilkan entri CHANGELOG.md dari riwayat git.

```bash
anote changelog
anote changelog --since v1.2.0
anote changelog --dry-run
```

## `anote docs`

Hasilkan dokumentasi untuk kode yang tidak terdokumentasi.

```bash
anote docs
anote docs src/api.ts
anote docs --style jsdoc
anote docs --dry-run
```

## `anote migrate`

Migrasi basis kode yang dibantu AI.

```bash
anote migrate --from "React 17" --to "React 18"
anote migrate --from "axios" --to "fetch"
anote migrate --dry-run
```

## `anote security`

Audit keamanan basis kode Anda (OWASP Top 10).

```bash
anote security
anote security --severity high
anote security --fix
```

## `anote perf`

Analisis kinerja.

```bash
anote perf
anote perf --focus "database,bundle"
anote perf --fix
```
