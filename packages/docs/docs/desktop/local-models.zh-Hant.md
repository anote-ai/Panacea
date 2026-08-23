# 本地模型

桌面應用程式支援透過 [Ollama](https://ollama.ai) 進行本地 LLM 推理。

## 設定

1. 從 [ollama.ai](https://ollama.ai) 安裝 Ollama
2. 下載模型：
   ```bash
   ollama pull llama3
   ollama pull mistral
   ```
3. 在桌面應用程式中，從模型下拉選單中選擇一個本地模型（以 `ollama/` 為前綴）

## 支援的模型

| 模型   | 下載命令                   |
|--------|---------------------------|
| Llama 3 | `ollama pull llama3`     |
| Mistral | `ollama pull mistral`    |
| Phi-3   | `ollama pull phi3`       |

本地模型完全在您的硬體上運行 — 沒有數據離開您的機器。
