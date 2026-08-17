# Wie Panacea funktioniert

Panacea führt eine **agentische Schleife** aus: Es liest Ihren Prompt, entscheidet, welche Tools aufgerufen werden, führt sie aus, liest die Ergebnisse und wiederholt dies — dabei streamt es seine Überlegungen und Änderungen zurück an Sie — bis die Aufgabe erledigt ist oder ein Rundenlimit erreicht wird.

## Die Tools

Standardmäßig kann der Agent von Panacea Folgendes aufrufen:

| Tool | Zweck |
|---|---|
| `Read` | Eine Datei lesen |
| `Write` | Eine Datei erstellen oder überschreiben |
| `Edit` | Eine gezielte Änderung an einer Datei vornehmen |
| `Bash` | Einen Shell-Befehl ausführen |
| `Glob` | Dateien nach Muster finden |
| `Grep` | Dateiinhalte durchsuchen |

Manche Befehle schränken diese Liste ein — `anote review` und `anote diff` erlauben zum Beispiel nur `Read`, `Glob`, `Grep` und `Bash`, da eine Überprüfung keine Dateien schreiben sollte.

## Runden und Komprimierung

Jedes Paar aus Tool-Aufruf/Antwort zählt als eine Runde. Der Agent stoppt nach `maxTurns` (Standard 30, konfigurierbar über `anote config set maxTurns <n>` oder `.anote.json`). Lange Sitzungen werden nach `compactAfterMessages` (Standard 40) komprimiert, um das Kontextfenster überschaubar zu halten.

## Streaming

Jede Oberfläche — CLI, VS Code, Web, Desktop — spricht mit demselben Backend-Endpunkt (`POST /api/chat/stream`), der die Antwort des Modells und die Tool-Aktivität per SSE in Echtzeit streamt. Sie sehen Dateilesevorgänge, Änderungen und Befehlsausgaben live, nicht nur die endgültige Antwort.

## Multi-Provider

Die Agenten-Schleife ist nicht an ein Modell gebunden. `anote ask --compare` führt denselben Prompt über mehrere Modelle nebeneinander aus, und `--model` akzeptiert bei den meisten Befehlen jeden konfigurierten Anbieter (`claude-sonnet-4-6`, `gpt-4.1`, `gemini-2.5-pro`, oder ein lokales `ollama/<model>`).

## Nächste Schritte

- [Berechtigungsmodi](../use-panacea/permission-modes.md) — steuern, ob der Agent vor dem Bearbeiten von Dateien oder Ausführen von Befehlen nachfragt
- [Panacea erweitern](extend.md) — CLAW.md und Hooks
- [CLI-Befehle](../cli/commands.md) — die vollständige Befehlsreferenz
