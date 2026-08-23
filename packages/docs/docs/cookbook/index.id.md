# Ikhtisar Buku Masak

Buku Masak Panacea adalah sekumpulan panduan implementasi yang menunjukkan bagaimana fitur-fitur platform Panacea bekerja di balik layar — pengambilan dokumen dan RAG, orkestrasi multi-agen, penagihan, server alat MCP, dan lainnya. Setiap panduan menunjuk pada file backend nyata yang terlibat dan menjelaskan cara menjalankan bagian sistem tersebut secara lokal.

Sumber: [anote-ai/Cookbook](https://github.com/anote-ai/Cookbook).

## Resep

| Resep | Deskripsi |
|---|---|
| [Dokumen Q&A + RAG](03-panacea-document-qa-rag.md) | Memahami pengambilan dokumen pribadi Panacea, pemulihan, dan alur kerja jawaban yang terarah |
| [Orkestrasi Multi-Agen](04-panacea-multi-agent-orchestration.md) | Pelajari bagaimana Panacea mengarahkan tugas melalui orkestrator, agen, kru, dan alur kerja |
| [Alat Koding AI](05-panacea-ai-coding-toolchain.md) | Jelajahi bagaimana Panacea memberikan bantuan koding melalui CLI, VS Code, dan SDK-nya |
| [Pengambilan Dokumen Multi-Modal](06-panacea-multimodal-ingestion.md) | Memahami bagaimana Panacea membuat gambar, audio, video, dan spreadsheet dapat dicari melalui pipeline RAG yang sama |
| [Gerbang API Kompatibel OpenAI](07-panacea-openai-compatible-gateway.md) | Arahkan alat berbasis OpenAI-SDK ke Panacea tanpa perubahan kode |
| [Penagihan, Kunci API & Pengukuran Kredit](08-panacea-billing-and-api-keys.md) | Pelajari bagaimana langganan Stripe, kunci API, dan pengukuran kredit per permintaan saling terkait |
| [Server Alat MCP](09-panacea-mcp-tool-server.md) | Mengekspos primitif dokumen/chat Panacea sebagai alat MCP standar untuk Claude Desktop dan klien MCP lainnya |
| [Bot Pesan Multi-Kanal](10-panacea-messaging-bots.md) | Ajukan pertanyaan koding Panacea dari Slack, SMS, dan WhatsApp |

## Menjalankan resep secara lokal

Sebagian besar resep dijalankan terhadap tumpukan Panacea yang lengkap:

```bash
cp packages/backend/.env.example packages/backend/.env
docker compose up --build
```

Lihat [Memulai](../getting-started/installation.md) untuk pengaturan lengkap, dan halaman masing-masing resep untuk langkah-langkah spesifiknya.
