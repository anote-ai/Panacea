# Mulai Cepat

## 1. Inisialisasi

```bash
anote init
```

Ini akan memandu Anda untuk mengatur kunci API dan penyedia LLM yang diinginkan.

## 2. Ajukan pertanyaan

```bash
# Pertanyaan umum
anote ask "bagaimana cara kerja otentikasi dalam kode ini?"

# Fokus pada sebuah file
anote ask --file src/auth.ts "jelaskan ini"

# Alirkan kode
cat src/handler.py | anote ask "apa yang bisa salah di sini?"
```

## 3. Perbaiki bug secara otomatis

```bash
# Perbaiki dan iterasi hingga tes lulus (hingga 5 putaran)
anote fix --loop --max-iterations 5
```

## 4. Indeks untuk pencarian semantik

```bash
# Indeks kode Anda (jalankan sekali, lalu tetap diperbarui)
anote index

# Cari secara semantik
anote search "validasi token JWT"
anote search "pool koneksi database"
```

## 5. Tinjau PR

```bash
anote review --pr 42
```

## 6. Hasilkan changelog

```bash
anote changelog --since v1.2.0
```
