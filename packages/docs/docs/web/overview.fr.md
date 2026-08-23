# Aperçu de l'application Web

L'application web Anote AI est une interface de chat de style ChatGPT qui se connecte au backend Anote.

## Fonctionnalités

- Mode clair et mode sombre (détecte automatiquement la préférence du système)
- Réponses en streaming via SSE
- Historique des sessions de chat dans une barre latérale réductible
- Sélecteur de modèle (Claude, GPT-4o, etc.)
- Téléchargement de documents et questions-réponses
- Design réactif

## Exécution en local

```bash
cd packages/web
npm install
npm run dev
```

L'application fonctionne à `http://localhost:3000` et proxy les appels API vers `http://localhost:5000`.
