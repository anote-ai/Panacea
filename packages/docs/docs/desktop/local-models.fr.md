# Modèles Locaux

L'application de bureau prend en charge l'inférence LLM locale via [Ollama](https://ollama.ai).

## Configuration

1. Installez Ollama depuis [ollama.ai](https://ollama.ai)
2. Téléchargez un modèle :
   ```bash
   ollama pull llama3
   ollama pull mistral
   ```
3. Dans l'application de bureau, sélectionnez un modèle local dans le menu déroulant des modèles (préfixé par `ollama/`)

## Modèles Prise en Charge

| Modèle | Commande de Téléchargement |
|-------|-----------------------------|
| Llama 3 | `ollama pull llama3` |
| Mistral | `ollama pull mistral` |
| Phi-3 | `ollama pull phi3` |

Les modèles locaux fonctionnent entièrement sur votre matériel — aucune donnée ne quitte votre machine.
