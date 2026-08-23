# Fonctionnalités de l'application Web

## Interface de chat

La vue principale du chat reflète le design de ChatGPT : une barre latérale gauche réductible avec l'historique des sessions, et un fil de messages centré avec une barre d'entrée en bas.

## Mode clair / sombre

Basculer avec le bouton en haut à droite. La préférence est conservée dans `localStorage`.

- **Clair** : arrière-plans blancs/gris clair, texte noir
- **Sombre** : arrière-plans `#212121`/`#2F2F2F`, texte blanc

## Streaming

L'entrée envoie une requête `POST /api/chat/stream` et lit la réponse SSE. Un bouton d'arrêt interrompt le flux en cours.

## Sessions

Chaque conversation est une session stockée côté serveur. Les sessions sont listées dans la barre latérale et persistent entre les chargements de page.
