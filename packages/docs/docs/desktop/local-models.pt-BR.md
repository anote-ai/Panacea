# Modelos Locais

O aplicativo de desktop suporta inferência LLM local via [Ollama](https://ollama.ai).

## Configuração

1. Instale o Ollama a partir de [ollama.ai](https://ollama.ai)
2. Baixe um modelo:
   ```bash
   ollama pull llama3
   ollama pull mistral
   ```
3. No aplicativo de desktop, selecione um modelo local no menu suspenso de modelos (prefixado com `ollama/`)

## Modelos Suportados

| Modelo  | Comando de Pull          |
|---------|--------------------------|
| Llama 3 | `ollama pull llama3`     |
| Mistral | `ollama pull mistral`     |
| Phi-3   | `ollama pull phi3`       |

Modelos locais são executados inteiramente no seu hardware — nenhum dado sai da sua máquina.
