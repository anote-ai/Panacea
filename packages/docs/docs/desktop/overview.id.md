# Ikhtisar Aplikasi Desktop

Aplikasi desktop Anote AI adalah asisten AI pribadi yang dapat berfungsi secara offline dan dibangun dengan Electron.

## Properti Utama

- **Pribadi**: semua data tetap di mesin Anda
- **Dapat berfungsi secara offline**: bekerja dengan model Ollama lokal
- **Lintas platform**: Windows, macOS, Linux
- **Backend terbundel**: backend Python Flask dikemas sebagai executable mandiri

## Arsitektur

```
Electron shell
  └─ React frontend (Vite + Tailwind)
  └─ Bundled Python backend (PyInstaller executable)
       └─ Flask API di port 5099
       └─ Basis data SQLite (lokal)
       └─ ChromaDB vector store (lokal)
```
