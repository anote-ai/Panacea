# Übersicht

**Ourogen** ist ein einheitlicher KI-Coding-Assistent und private Chatbot-Plattform. Er liest Ihren Code, bearbeitet Dateien, führt Befehle aus, überprüft PRs und beantwortet Fragen zu Ihren Dokumenten – verfügbar in Ihrem Terminal, IDE, Browser, Desktop-App und auf Ihrem Handy.

## Erste Schritte

Anote läuft auf mehreren Oberflächen: der CLI, VS Code, dem Web, Desktop und mobil. Wählen Sie eine der Optionen unten, um loszulegen. Die meisten Oberflächen kommunizieren mit dem gehosteten Anote-Backend oder Ihrer eigenen selbstgehosteten Instanz (siehe [Konfiguration](getting-started/configuration.md)).

=== "CLI"

    Die voll ausgestattete CLI, um direkt im Terminal mit Anote zu arbeiten. Stellen Sie Fragen, beheben Sie Fehler, überprüfen Sie PRs und durchsuchen Sie Ihren Code, ohne die Shell zu verlassen.

    ```bash
    npm install -g @anote-ai/anote
    ```

    Erfordert Node.js 18 oder höher. Dann in jedem Projekt:

    ```bash
    cd your-project
    anote init
    anote ask "erkläre diesen Code"
    ```

    `anote init` führt Sie durch die Einrichtung Ihres API-Schlüssels und des bevorzugten LLM-Anbieters.

    [Fahren Sie mit dem Schnellstart fort →](getting-started/quickstart.md)

=== "VS Code"

    Die VS Code-Erweiterung bringt eine Chat-Seitenleiste, Inline-Diff-Überprüfung und Streaming-Antworten direkt in Ihren Editor.

    Suchen Sie nach **"Anote"** im VS Code Extensions-Marktplatz oder installieren Sie es über:

    ```bash
    code --install-extension anote-ai.anote-ai-coding
    ```

    [Übersicht über die VS Code-Erweiterung →](vscode/overview.md)

=== "Web-App"

    Eine ChatGPT-ähnliche Browser-Chatoberfläche mit Dokumenten-Upload und RAG-unterstütztem Q&A. Selbst gehostet mit Docker Compose:

    ```bash
    git clone https://github.com/anote-ai/Panacea
    cd Panacea
    cp packages/backend/.env.example packages/backend/.env
    # Bearbeiten Sie .env mit Ihren API-Schlüsseln
    docker compose up
    ```

    Frontend: `http://localhost:3000` · Backend: `http://localhost:5000`

    [Übersicht über die Web-App →](web/overview.md)

=== "Desktop"

    Eine private, offline-fähige Electron-App. Alle Daten bleiben auf Ihrem Gerät, und sie funktioniert mit lokalen Ollama-Modellen, wenn Sie nicht zu einem gehosteten Anbieter aufrufen möchten.

    Laden Sie die neueste Version von [GitHub Releases](https://github.com/anote-ai/Panacea/releases) herunter – verfügbar für **macOS** (DMG), **Windows** (Installer) und **Linux** (AppImage/DEB/RPM).

    [Übersicht über die Desktop-App →](desktop/overview.md)

=== "Mobil"

    Ein nativer iOS- und Android-Chat-Client, der mit Expo erstellt wurde.

    ```bash
    cd packages/mobile
    npm install
    npx expo start
    ```

    Scannen Sie den QR-Code mit der Expo Go-App oder führen Sie ihn in einem Simulator aus.

    [Übersicht über die mobile App →](mobile/overview.md)

## Was Sie tun können

??? abstract "Fragen zu Ihrem Code stellen"

    ```bash
    anote ask "wie funktioniert die Authentifizierungsmiddleware?"
    anote ask --file src/auth.ts "erkläre diese Datei"
    anote ask --compare               # nebeneinander über mehrere Modelle
    cat src/handler.py | anote ask "was könnte hier schiefgehen?"
    ```

??? bug "Fehler automatisch beheben"

    `anote fix --loop` iteriert gegen Ihre Test-Suite – bis zu `--max-iterations` Runden – bis es besteht oder eine einzelne Datei mit `--file` behebt.

    ```bash
    anote fix --loop --max-iterations 5
    ```

??? example "Pull-Requests überprüfen"

    ```bash
    anote review --pr 42
    ```

    Überprüfungen auf Fehler, Sicherheitsprobleme und Qualität – lokal gegen ein Verzeichnis/eine Datei oder direkt an einen GitHub PR gepostet.

??? search "Durchsuchen Sie Ihren Code semantisch"

    ```bash
    anote index              # erstellen Sie einen TF-IDF-Index (einmal ausführen, dann aktuell halten)
    anote search "JWT-Token-Validierung"
    ```

??? question "Chat und Q&A über Ihre Dokumente"

    Laden Sie Dokumente in der [Web-App](web/overview.md) oder [Desktop-App](desktop/overview.md) hoch und stellen Sie Fragen dazu – RAG-unterstützt über `POST /api/documents/{id}/ask`.

??? tip "Überprüfen Sie auf Sicherheits- und Leistungsprobleme"

    ```bash
    anote security --severity high --fix
    anote perf --focus "datenbank,bundle" --fix
    ```

??? note "Changelogs und Dokumente generieren oder Migrationen durchführen"

    ```bash
    anote changelog --since v1.2.0
    anote docs src/api.ts --style jsdoc
    anote migrate --from "React 17" --to "React 18"
    ```

??? info "Überprüfen Sie Ihre Einrichtung"

    ```bash
    anote doctor
    ```

    Überprüft Node.js ≥ 18, `ANTHROPIC_API_KEY`, `.anote.json`, `CLAW.md` und git.

## Verwenden Sie Anote überall

| Ich möchte... | Beste Option |
|---|---|
| Von meinem Terminal aus arbeiten | [CLI](cli/overview.md) |
| Inline-KI-Hilfe in meinem Editor erhalten | [VS Code-Erweiterung](vscode/overview.md) |
| Mit Dokumenten in einem Browser chatten | [Web-App](web/overview.md) |
| Alles privat und offline halten | [Desktop-App](desktop/overview.md) – funktioniert mit lokalen Ollama-Modellen |
| Von meinem Handy aus chatten | [Mobile App](mobile/overview.md) |
| Anote aus meinem eigenen Code oder Skripten aufrufen | [TypeScript SDK](sdk/typescript.md) oder [Python SDK](sdk/python.md) |
| Direkt gegen die REST-API integrieren | [Backend-API](api/overview.md) |
| PR-Überprüfung oder CI-Checks automatisieren | [CLI: `anote review --pr`](cli/commands.md#anote-review) |

## Unterstützte LLM-Anbieter

- **Anthropic** — Claude (`claude-opus-4-8`, `claude-sonnet-4-6`, `claude-haiku-4-5`)
- **OpenAI** — GPT-4o, GPT-4o-mini
- **Google** — Gemini 2.0 Flash, Gemini 1.5 Pro
- **Ollama** — jedes lokale Modell (Llama 3, Mistral usw.)
- **xAI** — Grok

## Nächste Schritte

- [Schnellstart](getting-started/quickstart.md) — init, ask, fix, index, review und changelog in der Reihenfolge
- [Wie Panacea funktioniert](core-concepts/how-it-works.md) — der agentische Loop, Tools und Streaming
- [Berechtigungsmodi](use-panacea/permission-modes.md) — steuern, was der Agent tun kann, ohne zu fragen
- [Häufige Workflows](use-panacea/common-workflows.md) — Schritt-für-Schritt-Muster für alltägliche Aufgaben
- [Konfiguration](getting-started/configuration.md) — API-Schlüssel, Anbieter-Einrichtung und `~/.anote/config.json`
- [CLI-Befehle](cli/commands.md) — das vollständige Befehlsverzeichnis
- [Backend-API](api/overview.md) — die REST-Endpunkte, die jede Oberfläche antreiben
- [Architektur](development/architecture.md) — wie das Monorepo und das Backend zusammenpassen
- [Beitragen](development/contributing.md) — das Repository für die lokale Entwicklung einrichten
