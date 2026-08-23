# 本地模型

桌面应用程序通过 [Ollama](https://ollama.ai) 支持本地 LLM 推理。

## 设置

1. 从 [ollama.ai](https://ollama.ai) 安装 Ollama
2. 拉取模型：
   ```bash
   ollama pull llama3
   ollama pull mistral
   ```
3. 在桌面应用程序中，从模型下拉菜单中选择一个本地模型（以 `ollama/` 为前缀）

## 支持的模型

| 模型    | 拉取命令                |
|---------|-------------------------|
| Llama 3 | `ollama pull llama3`    |
| Mistral | `ollama pull mistral`    |
| Phi-3   | `ollama pull phi3`      |

本地模型完全在您的硬件上运行——没有数据离开您的机器。
