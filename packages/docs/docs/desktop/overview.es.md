# Descripción general de la aplicación de escritorio

La aplicación de escritorio Anote AI es un asistente de IA privado y capaz de funcionar sin conexión, construido con Electron.

## Propiedades clave

- **Privado**: todos los datos permanecen en su máquina
- **Capaz de funcionar sin conexión**: funciona con modelos locales de Ollama
- **Multiplataforma**: Windows, macOS, Linux
- **Backend empaquetado**: el backend de Python Flask se empaqueta como un ejecutable independiente

## Arquitectura

```
Electron shell
  └─ React frontend (Vite + Tailwind)
  └─ Backend de Python empaquetado (ejecutable de PyInstaller)
       └─ API de Flask en el puerto 5099
       └─ Base de datos SQLite (local)
       └─ Almacenamiento de vectores ChromaDB (local)
```
