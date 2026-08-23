# Modelos Locales

La aplicación de escritorio admite la inferencia LLM local a través de [Ollama](https://ollama.ai).

## Configuración

1. Instala Ollama desde [ollama.ai](https://ollama.ai)
2. Descarga un modelo:
   ```bash
   ollama pull llama3
   ollama pull mistral
   ```
3. En la aplicación de escritorio, selecciona un modelo local del menú desplegable de modelos (prefijado con `ollama/`)

## Modelos Soportados

| Modelo  | Comando de Descarga |
|---------|---------------------|
| Llama 3 | `ollama pull llama3` |
| Mistral | `ollama pull mistral` |
| Phi-3   | `ollama pull phi3` |

Los modelos locales se ejecutan completamente en tu hardware: ningún dato sale de tu máquina.
