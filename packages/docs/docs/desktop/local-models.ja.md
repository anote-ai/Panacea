# ローカルモデル

デスクトップアプリは、[Ollama](https://ollama.ai)を介してローカルLLM推論をサポートしています。

## セットアップ

1. [ollama.ai](https://ollama.ai)からOllamaをインストールします。
2. モデルをプルします：
   ```bash
   ollama pull llama3
   ollama pull mistral
   ```
3. デスクトップアプリで、モデルドロップダウンからローカルモデルを選択します（`ollama/`で始まる）。

## サポートされているモデル

| モデル | プルコマンド |
|-------|--------------|
| Llama 3 | `ollama pull llama3` |
| Mistral | `ollama pull mistral` |
| Phi-3 | `ollama pull phi3` |

ローカルモデルは完全にあなたのハードウェア上で実行されます — データはあなたのマシンを離れません。
