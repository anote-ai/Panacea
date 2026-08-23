# Aperçu de l'application de bureau

L'application de bureau Anote AI est un assistant IA privé, capable de fonctionner hors ligne, construit avec Electron.

## Propriétés clés

- **Privé** : toutes les données restent sur votre machine
- **Capable hors ligne** : fonctionne avec des modèles Ollama locaux
- **Multiplateforme** : Windows, macOS, Linux
- **Backend intégré** : le backend Python Flask est emballé en tant qu'exécutable autonome

## Architecture

```
Electron shell
  └─ React frontend (Vite + Tailwind)
  └─ Backend Python intégré (exécutable PyInstaller)
       └─ API Flask sur le port 5099
       └─ Base de données SQLite (locale)
       └─ Magasin de vecteurs ChromaDB (local)
```
