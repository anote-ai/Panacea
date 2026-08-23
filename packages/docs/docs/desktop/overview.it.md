# Panoramica dell'App Desktop

L'app desktop Anote AI è un assistente AI privato, in grado di funzionare offline, costruito con Electron.

## Proprietà Chiave

- **Privato**: tutti i dati rimangono sul tuo dispositivo
- **Capacità offline**: funziona con modelli Ollama locali
- **Cross-platform**: Windows, macOS, Linux
- **Backend integrato**: il backend Python Flask è confezionato come eseguibile autonomo

## Architettura

```
Electron shell
  └─ frontend React (Vite + Tailwind)
  └─ backend Python integrato (eseguibile PyInstaller)
       └─ API Flask sulla porta 5099
       └─ database SQLite (locale)
       └─ ChromaDB vector store (locale)
```
