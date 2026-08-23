# Gerbang API Kompatibel OpenAI Panacea

Resep ini menjelaskan cara mengarahkan alat apa pun yang dibangun terhadap OpenAI SDK ke Panacea — tanpa perubahan kode — sambil tetap mendapatkan akses ke ekstensi RAG spesifik Panacea seperti sumber dokumen yang terhubung.

## Apa yang akan Anda pelajari

- Bagaimana `AnoteOpenAI` mencerminkan antarmuka klien `openai.OpenAI` yang sebenarnya
- Cara mengunggah dokumen dan mendapatkan jawaban yang berbasis dokumen melalui API berbentuk chat-completions
- Cara streaming bekerja melalui Server-Sent Events (SSE), gaya OpenAI
- Di mana ekstensi spesifik Panacea (`anote_sources`, `anote_message_id`) muncul dalam respons

## Mengapa ini penting

Sejumlah besar alat yang ada — integrasi LangChain, skrip internal, kerangka agen pihak ketiga — ditulis berdasarkan bentuk OpenAI SDK (`client.chat.completions.create(...)`, `client.models.list()`). Daripada meminta setiap integrator untuk mempelajari SDK Panacea yang khusus, Panacea mengirimkan klien yang dapat langsung digunakan yang berbicara dengan antarmuka yang sama, sehingga tim dapat mengadopsi backend pribadi Panacea yang berbasis dokumen tanpa menulis ulang kode integrasi mereka.

## File Kunci Panacea

| File | Mengapa ini penting |
|---|---|
| `Panacea/backend/sdk/anoteai/openai_compat.py` | Klien `AnoteOpenAI`: `CompletionsClient`, `ModelsClient`, `DocumentsClient`, dan parser stream SSE |
| `Panacea/backend/sdk/anoteai/core.py` | Kelas SDK `PrivateChatbot` yang mendasari yang dibungkus oleh lapisan kompatibilitas |
| `Panacea/backend/sdk/anoteai/handlers/private_handlers.py` | Penanganan permintaan yang dibagikan dengan SDK asli |
| Rute server: `POST /v1/chat/completions`, `GET /v1/models`, `POST /v1/question-answer`, `POST /public/upload` | Endpoint berbentuk OpenAI (dan satu spesifik Panacea) yang dipanggil klien |

## Cara kerjanya

1. Buat instansi klien persis seperti SDK OpenAI, tetapi diarahkan ke backend Panacea Anda:

   ```python
   from anoteai.openai_compat import AnoteOpenAI

   client = AnoteOpenAI(
       api_key="your-anote-api-key",       # atau set ANOTE_API_KEY
       base_url="http://localhost:5000",    # atau https://api.anote.ai
   )
   ```

2. Untuk Q&A berbasis dokumen, unggah file terlebih dahulu — `client.documents.upload(...)` mengirimkan data formulir multipart ke `/public/upload` dan mengembalikan `chat_id`.
3. Ajukan pertanyaan dengan cara yang sama seperti Anda memanggil SDK OpenAI, melewatkan `chat_id` melalui `extra_body` sehingga server tahu dokumen mana yang harus diambil:

   ```python
   upload_resp = client.documents.upload("path/to/report.pdf")
   chat_id = upload_resp["chat_id"]

   response = client.chat.completions.create(
       model="gpt-4o",
       messages=[{"role": "user", "content": "Ringkaskan temuan kunci."}],
       extra_body={"chat_id": chat_id},
   )
   print(response.choices[0].message.content)
   print("Sumber:", response.anote_sources)
   ```

4. Respons dipetakan ke dalam dataclass yang mencerminkan SDK OpenAI yang sebenarnya (`ChatCompletion`, `Choice`, `Message`, `Usage`), ditambah dua ekstensi Panacea: `anote_message_id` dan `anote_sources` (potongan/kutipan yang diambil yang mendukung jawaban).
5. Lewati `stream=True` untuk mendapatkan generator objek `ChatCompletionChunk` yang diparsing dari baris SSE `text/event-stream` (`data: {...}` per token, diakhiri dengan `data: [DONE]`) — bentuk yang sama yang dihasilkan oleh klien streaming OpenAI.
6. `client.models.list()` memanggil `GET /v1/models` untuk penemuan model, mengembalikan objek `Model`/`ModelList` seperti SDK OpenAI.

## Jalankan secara lokal

Dari root workspace (`anote/panacea`):

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

Instal satu ketergantungan klien dan set kunci API Anda:

```bash
pip install requests
export ANOTE_API_KEY=your_api_key_here   # macOS/Linux
set ANOTE_API_KEY=your_api_key_here      # Windows cmd
```

### Panduan Minimal

```python
from anoteai.openai_compat import AnoteOpenAI

client = AnoteOpenAI(base_url="http://localhost:5000")

# Obrolan biasa, tanpa dokumen:
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Apa ibu kota Prancis?"}],
)
print(response.choices[0].message.content)

# Streaming:
for chunk in client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hitung sampai lima."}],
    stream=True,
):
    for choice in chunk.choices:
        if choice.delta.content:
            print(choice.delta.content, end="", flush=True)
```

## Catatan untuk buku masak

Resep ini adalah pelengkap yang baik untuk resep 03 — ini adalah kemampuan Q&A/RAG berbasis dokumen yang sama, tetapi diekspos melalui antarmuka yang dapat dikonsumsi oleh alat berbasis OpenAI-SDK yang ada tanpa modifikasi. Perlu dicatat kepada pembaca bahwa `DocumentsClient.upload()`/`question_answer()` adalah pembantu spesifik Panacea yang dilapisi di atas inti yang kompatibel dengan OpenAI, bukan bagian dari spesifikasi OpenAI itu sendiri.
