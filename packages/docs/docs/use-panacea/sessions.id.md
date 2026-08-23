# Mengelola Sesi

Setiap percakapan `anote chat` disimpan secara lokal sebagai sesi — pesan, penggunaan token, dan direktori kerja.

## Daftar sesi

```bash
anote sessions list
anote sessions ls --limit 50
```

```
Sesi yang disimpan (3):
  a1b2c3d4  12 pesan  in=4,200 out=1,800  10m yang lalu  /Users/you/project
  e5f6a7b8  4 pesan   in=900 out=400      2j yang lalu   /Users/you/other-project
```

## Tampilkan sesi

```bash
anote sessions show a1b2c3d4
anote sessions show a1b2c3d4 --limit 50   # lebih banyak riwayat pesan
```

Mencetak percakapan, total token, dan direktori kerja untuk sesi tersebut. Anda dapat melewatkan prefiks pendek dari ID sesi daripada yang lengkap.

## Hapus sesi

```bash
anote sessions delete a1b2c3d4
anote sessions rm a1b2c3d4
```

## Langkah selanjutnya

- [Alur kerja umum](common-workflows.md)
- [Cara kerja Panacea](../core-concepts/how-it-works.md) — giliran, kompaksi, dan bagaimana panjang sesi mempengaruhi konteks
