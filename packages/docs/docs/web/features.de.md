# Webanwendungsfunktionen

## Chat-Schnittstelle

Die Hauptansicht des Chats spiegelt das Design von ChatGPT wider: eine einklappbare linke Seitenleiste mit Sitzungsverlauf und einen zentrierten Nachrichtenstrang mit einer Eingabeleiste am unteren Rand.

## Hell-/Dunkelmodus

Umschalten mit der Schaltfläche oben rechts. Die Präferenz wird in `localStorage` gespeichert.

- **Hell**: weiße/hellgraue Hintergründe, schwarzer Text
- **Dunkel**: `#212121`/`#2F2F2F` Hintergründe, weißer Text

## Streaming

Die Eingabe sendet eine `POST /api/chat/stream`-Anfrage und liest die SSE-Antwort. Eine Stopptaste bricht den Stream ab.

## Sitzungen

Jedes Gespräch ist eine Sitzung, die serverseitig gespeichert wird. Sitzungen werden in der Seitenleiste aufgelistet und bleiben über Seitenladevorgänge hinweg bestehen.
