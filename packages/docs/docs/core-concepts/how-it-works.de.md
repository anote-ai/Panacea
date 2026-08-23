# Wie Panacea funktioniert

Panacea führt eine **agentische Schleife** aus: Es liest Ihren Prompt, entscheidet, welche Werkzeuge aufgerufen werden sollen, führt sie aus, liest die Ergebnisse und wiederholt dies — streamt sein Denken und seine Änderungen zurück zu Ihnen — bis die Aufgabe erledigt ist oder es ein Wendepunktlimit erreicht.

## Die Werkzeuge

Standardmäßig kann der Agent von Panacea folgende Werkzeuge aufrufen:

| Werkzeug | Zweck |
|---|---|
| `Read` | Eine Datei lesen |
| `Write` | Eine Datei erstellen oder überschreiben |
| `Edit` | Eine gezielte Änderung an einer Datei vornehmen |
| `Bash` | Einen Shell-Befehl ausführen |
| `Glob` | Dateien nach Muster finden |
| `Grep` | Dateiinhalte durchsuchen |

Einige Befehle schränken diese Liste ein — `anote review` und `anote diff` erlauben beispielsweise nur `Read`, `Glob`, `Grep` und `Bash`, da eine Überprüfung keine Dateien schreiben sollte.

## Wendepunkte und Kompaktierung

Jedes Werkzeugaufruf/Antwort-Paar zählt als ein Wendepunkt. Der Agent stoppt nach `maxTurns` (Standard 30, konfigurierbar über `anote config set maxTurns <n>` oder `.anote.json`). Lange Sitzungen werden nach `compactAfterMessages` (Standard 40) kompakt gehalten, um das Kontextfenster handhabbar zu halten.

## Streaming

Jede Oberfläche — CLI, VS Code, Web, Desktop — kommuniziert mit demselben Backend-Endpunkt (`POST /api/chat/stream`), der die Antwort des Modells und die Aktivitäten der Werkzeuge über SSE streamt, während sie stattfinden. Sie sehen Datei-Lesungen, Änderungen und Befehlsausgaben live, nicht nur die endgültige Antwort.

## Multi-Anbieter

Die Agentenschleife ist nicht an ein Modell gebunden. `anote ask --compare` führt denselben Prompt nebeneinander über mehrere Modelle aus, und `--model` bei den meisten Befehlen akzeptiert jeden konfigurierten Anbieter (`claude-sonnet-4-6`, `gpt-4.1`, `gemini-2.5-pro` oder ein lokales `ollama/<model>`).

## Nächste Schritte

- [Berechtigungsmodi](../use-panacea/permission-modes.md) — steuern, ob der Agent vor dem Bearbeiten oder Ausführen von Befehlen fragt
- [Panacea erweitern](extend.md) — CLAW.md und Hooks
- [CLI-Befehle](../cli/commands.md) — das vollständige Befehlsverzeichnis
