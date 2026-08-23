# SDK Python

Klien Python tersedia melalui paket `anoteai` (bagian dari repositori Anote-Product).

## Instalasi

```bash
pip install anoteai
```

## Penggunaan

```python
from anoteai import Anote

client = Anote(api_key="sk-ai-...")

# Metode publik yang ada mengautentikasi dengan Authorization: Bearer sk-ai-...
result = client.classify(document_id="doc_123", labels=["contract", "invoice"])
answer = client.answer(document_id="doc_123", question="Berapa jumlah pembayaran?")
```

Buat kunci API dari Pengaturan -> Kunci API. Kunci dalam bentuk teks biasa ditampilkan sekali; setelah itu hanya prefiks kunci yang ditampilkan.

Biaya kredit:

| Operasi | Kredit |
| --- | ---: |
| Unggah dokumen | 1 per file atau URL |
| Pesan obrolan / Q&A | 1 per permintaan |
| Penyelesaian obrolan yang kompatibel dengan OpenAI | 1 per permintaan |

Tangani kesalahan API berdasarkan kode status:

| Status | Arti |
| --- | --- |
| 401 | Kunci API hilang atau tidak valid |
| 402 | Kredit tidak cukup |
| 429 | Batas laju per kunci terlampaui |

Lihat [repositori Anote-Product](https://github.com/anote-ai/anote-product) untuk dokumentasi SDK lengkap.
