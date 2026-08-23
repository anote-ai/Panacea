# Lokale Modelle

Die Desktop-App unterstützt lokale LLM-Inferenz über [Ollama](https://ollama.ai).

## Einrichtung

1. Installieren Sie Ollama von [ollama.ai](https://ollama.ai)
2. Laden Sie ein Modell herunter:
   ```bash
   ollama pull llama3
   ollama pull mistral
   ```
3. Wählen Sie in der Desktop-App ein lokales Modell aus dem Dropdown-Menü (mit `ollama/` vorangestellt)

## Unterstützte Modelle

| Modell | Pull-Befehl |
|-------|--------------|
| Llama 3 | `ollama pull llama3` |
| Mistral | `ollama pull mistral` |
| Phi-3 | `ollama pull phi3` |

Lokale Modelle laufen vollständig auf Ihrer Hardware — keine Daten verlassen Ihren Computer.
