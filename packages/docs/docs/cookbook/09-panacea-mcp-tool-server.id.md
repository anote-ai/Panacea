# Panacea MCP Tool Server

Resep ini menjelaskan bagaimana Panacea mengekspos primitif dokumen/obrolan sebagai alat [Model Context Protocol](https://modelcontextprotocol.io/) (MCP) standar, sehingga klien yang kompatibel dengan MCP (Claude Desktop, host MCP lainnya) dapat menggunakan kemampuan pengambilan dan riwayat obrolan Panacea secara langsung.

## Apa yang akan Anda pelajari

- Perbedaan antara permukaan MCP ini dan arsitektur pendaftaran agen/alat internal dari resep 04
- Operasi dokumen dan obrolan mana yang diekspos sebagai alat MCP
- Bagaimana pengambilan dokumen tetap non-blocking melalui tugas jarak jauh Ray
- Mengapa alat SQL passthrough mentah adalah pertimbangan keamanan yang perlu diperhatikan

## Mengapa ini penting

Resep 04 membahas bagaimana *orkestrator internal* Panacea mendaftarkan alat untuk agen-agen miliknya. Ini adalah permukaan integrasi yang berbeda: ini mengemas fungsi dokumen/obrolan yang sama sebagai **alat MCP standar eksternal** yang dapat dipanggil oleh klien MCP mana pun — tidak diperlukan kontrak SDK atau API khusus Panacea, hanya protokol MCP.

## File-file Kunci Panacea

| File | Mengapa itu penting |
|---|---|
| `Panacea/backend/mcp/mcp_server.py` | `FastMCP("Document Agent Server")` — mendefinisikan sembilan alat MCP |
| `Panacea/backend/api_endpoints/financeGPT/chatbot_endpoints.py` | Fungsi-fungsi yang berhadapan dengan DB yang dibungkus oleh setiap alat MCP (`get_relevant_chunks`, `add_document_to_db`, `chunk_document`, dll.) |
| `Panacea/backend/database/db.py` | `get_db_connection` — digunakan langsung oleh alat `execute_database_query` |

## Cara kerjanya

1. `mcp_server.py` menginisialisasi Ray (`ray.init(...)`) dan sebuah instance server `FastMCP` bernama `"Document Agent Server"`.
2. Setiap fungsi yang didekorasi dengan `@mcp.tool()` membungkus fungsi Panacea yang ada dan mengembalikan hasil teks biasa atau string kesalahan — bentuk yang diharapkan kembali oleh panggilan alat LLM:
   - `retrieve_relevant_chunks(query, chat_id, user_email, k=2)` — pencarian semantik atas dokumen obrolan melalui `get_relevant_chunks`
   - `ingest_document(text, document_name, chat_id, chunk_size=1000)` — mendaftarkan dokumen melalui `add_document_to_db`
   - `list_documents(chat_id, user_email)` / `delete_document(doc_id, user_email)` — manajemen dokumen
   - `add_message` / `get_chat_history` — membaca/menulis riwayat obrolan
   - `add_sources_to_message` — melampirkan kutipan ke pesan yang disimpan
   - `extract_text_from_url(url)` — mengambil dan mengembalikan konten teks dari URL
   - `execute_database_query(query, params)` — SQL passthrough mentah (lihat catatan keamanan di bawah)
3. `ingest_document` tidak memblokir pada penggalian — ia memanggil `chunk_document.remote(text, chunk_size, doc_id)`, sebuah tugas jarak jauh Ray, sehingga dokumen besar diproses secara asinkron sementara panggilan alat kembali segera.
4. Menjalankan `python backend/mcp/mcp_server.py` memulai `mcp.run()`, yang melayani alat-alat ini melalui transportasi stdio MCP — siap untuk klien MCP diluncurkan dan terhubung.
5. Klien MCP (misalnya Claude Desktop) yang dikonfigurasi untuk meluncurkan skrip ini mendapatkan akses ke sembilan alat secara otomatis, tanpa menulis kode integrasi khusus Panacea.

### Catatan keamanan

`execute_database_query` mengeksekusi string SQL sembarang terhadap koneksi produksi tanpa daftar izin atau pembatasan baca-saja — kueri `SELECT` mengembalikan baris sebagai JSON, apa pun yang lain mengkomit dan mengembalikan jumlah baris yang terpengaruh. Perlakukan ini sebagai wilayah hak akses minimal: jika Anda mengekspos server ini ke klien MCP yang tidak sepenuhnya Anda percayai, baik hapus alat ini atau batasi pengguna DB-nya hanya untuk akses baca pada tabel yang tidak sensitif.

## Jalankan secara lokal

Dari root workspace (`anote/panacea`):

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build   # menghidupkan MySQL, Redis, Tika, dan backend
```

Server MCP membutuhkan `fastmcp` (belum dipasang di `backend/requirements.txt` — instal secara terpisah) dan `ray>=2.9.0` (sudah ada di `backend/requirements.txt`):

```bash
pip install fastmcp
cd Panacea/backend
python mcp/mcp_server.py
```

### Hubungkan klien MCP

Arahkan klien yang kompatibel dengan MCP ke skrip, misalnya di `claude_desktop_config.json` Claude Desktop:

```json
{
  "mcpServers": {
    "panacea-documents": {
      "command": "python",
      "args": ["/absolute/path/to/Panacea/backend/mcp/mcp_server.py"]
    }
  }
}
```

Mulai ulang klien, dan sembilan alat di atas menjadi tersedia untuk dipanggil dari obrolan.

## Catatan untuk buku masak

Tindak lanjut yang baik untuk resep 04 — kontras pendaftaran alat internal (`register_tool()` di dalam orkestrator) dengan permukaan MCP eksternal ini. Juga perlu dicatat sebagai celah bagi pembaca: `fastmcp` belum terdaftar di `backend/requirements.txt`, jadi perlu instalasi manual sampai itu diperbaiki di hulu.
