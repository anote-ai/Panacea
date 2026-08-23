# Model Lokal

Aplikasi desktop mendukung inferensi LLM lokal melalui [Ollama](https://ollama.ai).

## Pengaturan

1. Instal Ollama dari [ollama.ai](https://ollama.ai)
2. Tarik model:
   ```bash
   ollama pull llama3
   ollama pull mistral
   ```
3. Di aplikasi desktop, pilih model lokal dari dropdown model (diberi awalan `ollama/`)

## Model yang Didukung

| Model   | Perintah Tarik         |
|---------|------------------------|
| Llama 3 | `ollama pull llama3`   |
| Mistral | `ollama pull mistral`   |
| Phi-3   | `ollama pull phi3`     |

Model lokal berjalan sepenuhnya di perangkat keras Anda — tidak ada data yang meninggalkan mesin Anda.
