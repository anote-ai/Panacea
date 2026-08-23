# Modelli Locali

L'app desktop supporta l'inferenza LLM locale tramite [Ollama](https://ollama.ai).

## Configurazione

1. Installa Ollama da [ollama.ai](https://ollama.ai)
2. Scarica un modello:
   ```bash
   ollama pull llama3
   ollama pull mistral
   ```
3. Nell'app desktop, seleziona un modello locale dal menu a discesa dei modelli (prefissato con `ollama/`)

## Modelli Supportati

| Modello | Comando di Scaricamento |
|---------|-------------------------|
| Llama 3 | `ollama pull llama3` |
| Mistral | `ollama pull mistral` |
| Phi-3 | `ollama pull phi3` |

I modelli locali vengono eseguiti interamente sul tuo hardware — nessun dato lascia la tua macchina.
