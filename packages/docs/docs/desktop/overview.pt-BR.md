# Visão Geral do Aplicativo Desktop

O aplicativo desktop Anote AI é um assistente de IA privado e capaz de funcionar offline, construído com Electron.

## Propriedades Principais

- **Privado**: todos os dados permanecem em sua máquina
- **Capaz de funcionar offline**: funciona com modelos locais do Ollama
- **Multiplataforma**: Windows, macOS, Linux
- **Backend empacotado**: backend Python Flask é empacotado como um executável independente

## Arquitetura

```
Shell do Electron
  └─ Frontend React (Vite + Tailwind)
  └─ Backend Python empacotado (executável PyInstaller)
       └─ API Flask na porta 5099
       └─ Banco de dados SQLite (local)
       └─ Armazenamento de vetores ChromaDB (local)
```
