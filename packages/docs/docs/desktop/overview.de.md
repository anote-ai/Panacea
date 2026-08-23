# Desktop-App-Übersicht

Die Anote AI Desktop-App ist ein privater, offline-fähiger KI-Assistent, der mit Electron erstellt wurde.

## Hauptmerkmale

- **Privat**: Alle Daten bleiben auf Ihrem Gerät
- **Offline-fähig**: Funktioniert mit lokalen Ollama-Modellen
- **Plattformübergreifend**: Windows, macOS, Linux
- **Integrierter Backend**: Python Flask-Backend ist als eigenständige ausführbare Datei verpackt

## Architektur

```
Electron-Shell
  └─ React-Frontend (Vite + Tailwind)
  └─ Integriertes Python-Backend (PyInstaller ausführbare Datei)
       └─ Flask-API auf Port 5099
       └─ SQLite-Datenbank (lokal)
       └─ ChromaDB-Vektorspeicher (lokal)
```
