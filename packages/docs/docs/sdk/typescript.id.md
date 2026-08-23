# SDK TypeScript

`@anote-ai/sdk` adalah klien TypeScript/JavaScript yang terketik untuk Anote REST API. Gunakan ini ketika Anda ingin memanggil Anote secara programatis — dari skrip, layanan backend, atau aplikasi Anda sendiri — alih-alih melalui CLI atau aplikasi web.

!!! note "Berbicara dengan backend lokal"
    Secara default, klien mengarah ke `https://api.anote.ai`. Jika Anda menjalankan backend dari repositori ini secara lokal (`docker compose up`, atau `make dev-backend`), berikan `baseUrl: "http://localhost:5050"` (atau `:5000` jika Anda tidak menggunakan penggantian port) — lihat [Memulai → Konfigurasi](../getting-started/configuration.md).

## Apa yang Anda Butuhkan

- Node.js 18+
- Akun Anote (daftar melalui `POST /auth/register` atau halaman Daftar aplikasi web)
- Kunci API (Langkah 2 di bawah)

## 1. Instal

```bash
npm install @anote-ai/sdk
```

## 2. Dapatkan kunci API

Belum ada UI Pengaturan untuk kunci API, jadi buat satu langsung terhadap backend. Pertama, masuk untuk mendapatkan JWT, lalu gunakan untuk membuat kunci:

```bash
# Masuk untuk mendapatkan JWT
curl -X POST http://localhost:5050/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "you@example.com", "password": "..."}'
# → { "access_token": "eyJ..." }

# Gunakan JWT untuk membuat kunci API
curl -X POST http://localhost:5050/api/user/api-keys \
  -H "Authorization: Bearer eyJ..."
# → { "key": "ak-..." }
```

Simpan nilai `ak-...` itu — hanya dikembalikan sekali, pada saat pembuatan.

## 3. Inisialisasi klien

```ts
import { AnoteClient } from "@anote-ai/sdk";

const client = new AnoteClient({
  apiKey: "ak-...",
  baseUrl: "http://localhost:5050", // hilangkan untuk menggunakan https://api.anote.ai
});
```

`apiKey` adalah satu-satunya opsi yang diperlukan. Tinggalkan `baseUrl` saat Anda mengarah ke API produksi.

## 4. Kirim pesan pertama Anda

```ts
const { result, usage } = await client.chat("Jelaskan kode ini");

console.log(result);
console.log(`Menggunakan ${usage.inputTokens} token input / ${usage.outputTokens} token output`);
```

`chat()` adalah panggilan non-streaming — ia menunggu respons penuh, yang Anda inginkan untuk skrip dan otomatisasi. Berikan `cwd`, `model`, atau `tools` dalam argumen kedua untuk menentukan direktori kerja, memilih model, atau membatasi alat yang dapat digunakan AI:

```ts
await client.chat("Daftar TODO di file ini", {
  cwd: "/path/to/project",
  model: "claude-sonnet-4-6",
  tools: ["Read", "Grep"],
});
```

## Tugas Umum

**Daftar dan periksa sesi sebelumnya**

```ts
const sessions = await client.listSessions();
const { history } = await client.getSessionMessages(sessions[0].sessionId);
```

**Cari di seluruh riwayat sesi**

```ts
const { results } = await client.search("logika otentikasi");
```

**Periksa penggunaan dan kuota Anda**

```ts
const usage = await client.getUsage();
console.log(`${usage.remaining.requests} permintaan tersisa bulan ini`);
```

**Bagikan sesi sebagai tautan hanya-baca**

```ts
const { shareUrl } = await client.shareSession(sessions[0].sessionId);
```

**Tangani kesalahan**

Setiap respons non-2xx melempar `AnoteError`, yang membawa status HTTP dan tubuh respons yang diparsing:

```ts
import { AnoteClient, AnoteError } from "@anote-ai/sdk";

try {
  await client.chat("...");
} catch (err) {
  if (err instanceof AnoteError) {
    console.error(err.status, err.message); // misalnya 429, "Kuota bulanan terlampaui"
  }
}
```

**Periksa keberlangsungan server (tidak memerlukan otentikasi)**

```ts
const health = await client.health();
```

## Referensi API

### `new AnoteClient(options)`

| Opsi | Tipe | Diperlukan | Deskripsi |
|---|---|---|---|
| `apiKey` | `string` | ✓ | Kunci API dari Langkah 2, dimulai dengan `ak-` |
| `baseUrl` | `string` | | URL Server (default: `https://api.anote.ai`) |

### Metode

| Metode | Deskripsi |
|--------|-------------|
| `chat(message, options?)` | Kirim pesan, dapatkan respons lengkap dari AI |
| `listSessions()` | Daftar semua sesi obrolan |
| `getSessionMessages(id)` | Dapatkan riwayat pesan untuk sebuah sesi |
| `deleteSession(id)` | Hapus sebuah sesi |
| `shareSession(id)` | Buat tautan hanya-baca yang dapat dibagikan |
| `search(query, limit?)` | Pencarian teks penuh di seluruh sesi |
| `getUsage()` | Penggunaan bulan ini + kuota |
| `health()` | Pemeriksaan keberlangsungan server (tidak memerlukan otentikasi) |

## Langkah Selanjutnya

- [Ikhtisar API Backend](../api/overview.md) — endpoint REST di bawah SDK ini
- [Ikhtisar CLI](../cli/overview.md) — untuk penggunaan interaktif/terminal alih-alih skrip
