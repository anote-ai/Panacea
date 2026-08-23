# Caratteristiche dell'App Web

## Interfaccia Chat

La vista principale della chat rispecchia il design di ChatGPT: una barra laterale sinistra collassabile con la cronologia delle sessioni e un thread di messaggi centrato con una barra di input in basso.

## Modalità Chiara / Scura

Attiva con il pulsante in alto a destra. La preferenza è memorizzata in `localStorage`.

- **Chiara**: sfondi bianchi/grigi chiari, testo nero
- **Scura**: sfondi `#212121`/`#2F2F2F`, testo bianco

## Streaming

L'input invia una richiesta `POST /api/chat/stream` e legge la risposta SSE. Un pulsante di stop interrompe lo streaming a metà.

## Sessioni

Ogni conversazione è una sessione memorizzata lato server. Le sessioni sono elencate nella barra laterale e persistono tra i caricamenti della pagina.
