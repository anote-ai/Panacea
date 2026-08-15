# Übersicht

**Anote AI** ist ein einheitlicher KI-Coding-Assistent und eine private Chat-Plattform. Es liest Ihre Codebase, bearbeitet Dateien, führt Befehle aus, überprüft Pull Requests und beantwortet Fragen zu Ihren Dokumenten — verfügbar in Ihrem Terminal, Ihrer IDE, Ihrem Browser, Ihrer Desktop-App und Ihrem Telefon.

## Erste Schritte

Anote läuft auf mehreren Oberflächen: CLI, VS Code, Web, Desktop und Mobile. Wählen Sie unten eine aus, um loszulegen. Die meisten Oberflächen kommunizieren mit dem gehosteten Anote-Backend oder Ihrer eigenen selbst gehosteten Instanz (siehe [Konfiguration](getting-started/configuration.md)).

=== "CLI"

    Die voll ausgestattete CLI für die Arbeit mit Anote direkt in Ihrem Terminal. Stellen Sie Fragen, beheben Sie Bugs, überprüfen Sie Pull Requests und durchsuchen Sie Ihre Codebase, ohne die Shell zu verlassen.

    ```bash
    npm install -g @anote-ai/anote
    ```

    Erfordert Node.js 18 oder neuer. Dann, in jedem Projekt:

    ```bash
    cd your-project
    anote init
    anote ask "explain this codebase"
    ```

    `anote init` führt Sie durch die Einrichtung Ihres API-Schlüssels und bevorzugten LLM-Anbieters.

    [Weiter mit dem Schnellstart →](getting-started/quickstart.md)

=== "VS Code"

    Die VS Code-Erweiterung bringt eine Chat-Seitenleiste, Inline-Diff-Überprüfung und Streaming-Antworten direkt in Ihren Editor.

    Suchen Sie nach **„Anote"** im VS Code Extensions Marketplace, oder installieren Sie über:

    ```bash
    code --install-extension anote-ai.anote-ai-coding
    ```

    [VS-Code-Erweiterung Übersicht →](vscode/overview.md)

=== "Web-App"

    Eine browserbasierte Chat-Oberfläche im ChatGPT-Stil mit Dokumenten-Upload und RAG-gestützten Fragen und Antworten. Selbst hosten mit Docker Compose:

    ```bash
    git clone https://github.com/anote-ai/Panacea
    cd Panacea
    cp packages/backend/.env.example packages/backend/.env
    # .env mit Ihren API-Schlüsseln bearbeiten
    docker compose up
    ```

    Frontend: `http://localhost:3000` · Backend: `http://localhost:5000`

    [Web-App Übersicht →](web/overview.md)

=== "Desktop"

    Eine private, offline-fähige Electron-App. Alle Daten bleiben auf Ihrem Rechner, und sie funktioniert mit lokalen Ollama-Modellen, wenn Sie keinen gehosteten Anbieter nutzen möchten.

    Laden Sie die neueste Version von [GitHub Releases](https://github.com/anote-ai/Panacea/releases) herunter — verfügbar für **macOS** (DMG), **Windows** (Installer) und **Linux** (AppImage/DEB/RPM).

    [Desktop-App Übersicht →](desktop/overview.md)

=== "Mobile"

    Ein nativer iOS- und Android-Chat-Client, gebaut mit Expo.

    ```bash
    cd packages/mobile
    npm install
    npx expo start
    ```

    Scannen Sie den QR-Code mit der Expo-Go-App, oder führen Sie ihn in einem Simulator aus.

    [Mobile-App Übersicht →](mobile/overview.md)

## Was Sie tun können

??? abstract "Fragen zu Ihrer Codebase stellen"

    ```bash
    anote ask "how does the authentication middleware work?"
    anote ask --file src/auth.ts "explain this file"
    anote ask --compare               # Vergleich mehrerer Modelle nebeneinander
    cat src/handler.py | anote ask "what could go wrong here?"
    ```

??? bug "Bugs automatisch beheben"

    `anote fix --loop` iteriert gegen Ihre Testsuite — bis zu `--max-iterations` Runden — bis sie besteht, oder behebt eine einzelne Datei mit `--file`.

    ```bash
    anote fix --loop --max-iterations 5
    ```

??? example "Pull Requests überprüfen"

    ```bash
    anote review --pr 42
    ```

    Überprüfungen auf Bugs, Sicherheitsprobleme und Qualität — lokal gegen ein Verzeichnis/eine Datei, oder direkt auf einen GitHub-PR gepostet.

??? search "Codebase semantisch durchsuchen"

    ```bash
    anote index              # TF-IDF-Index erstellen (einmalig, danach aktuell halten)
    anote search "JWT token validation"
    ```

??? question "Chat und Fragen zu Ihren Dokumenten"

    Laden Sie Dokumente in der [Web-App](web/overview.md) oder [Desktop-App](desktop/overview.md) hoch und stellen Sie Fragen dazu — RAG-gestützt über `POST /api/documents/{id}/ask`.

??? tip "Sicherheit und Performance prüfen"

    ```bash
    anote security --severity high --fix
    anote perf --focus "database,bundle" --fix
    ```

??? note "Changelogs und Dokumentation generieren, oder Migrationen durchführen"

    ```bash
    anote changelog --since v1.2.0
    anote docs src/api.ts --style jsdoc
    anote migrate --from "React 17" --to "React 18"
    ```

??? info "Setup überprüfen"

    ```bash
    anote doctor
    ```

    Prüft Node.js ≥ 18, `ANTHROPIC_API_KEY`, `.anote.json`, `CLAW.md` und git.

## Anote überall nutzen

| Ich möchte... | Beste Option |
|---|---|
| Von meinem Terminal aus arbeiten | [CLI](cli/overview.md) |
| KI-Hilfe direkt in meinem Editor | [VS-Code-Erweiterung](vscode/overview.md) |
| Mit Dokumenten im Browser chatten | [Web-App](web/overview.md) |
| Alles privat und offline halten | [Desktop-App](desktop/overview.md) — funktioniert mit lokalen Ollama-Modellen |
| Vom Telefon aus chatten | [Mobile-App](mobile/overview.md) |
| Anote aus eigenem Code oder Skripten aufrufen | [TypeScript SDK](sdk/typescript.md) oder [Python SDK](sdk/python.md) |
| Direkt gegen die REST-API integrieren | [Backend-API](api/overview.md) |
| PR-Überprüfung oder CI-Checks automatisieren | [CLI: `anote review --pr`](cli/commands.md#anote-review) |

## Unterstützte LLM-Anbieter

- **Anthropic** — Claude (`claude-opus-4-8`, `claude-sonnet-4-6`, `claude-haiku-4-5`)
- **OpenAI** — GPT-4o, GPT-4o-mini
- **Google** — Gemini 2.0 Flash, Gemini 1.5 Pro
- **Ollama** — jedes lokale Modell (Llama 3, Mistral, usw.)
- **xAI** — Grok

## Nächste Schritte

- [Schnellstart](getting-started/quickstart.md) — init, ask, fix, index, review und changelog der Reihe nach
- [Wie Panacea funktioniert](core-concepts/how-it-works.md) — die agentische Schleife, Tools und Streaming
- [Berechtigungsmodi](use-panacea/permission-modes.md) — steuern, was der Agent ohne Rückfrage tun darf
- [Häufige Workflows](use-panacea/common-workflows.md) — Schritt-für-Schritt-Muster für alltägliche Aufgaben
- [Konfiguration](getting-started/configuration.md) — API-Schlüssel, Anbieter-Setup und `~/.anote/config.json`
- [CLI-Befehle](cli/commands.md) — die vollständige Befehlsreferenz
- [Backend-API](api/overview.md) — die REST-Endpunkte hinter jeder Oberfläche
- [Architektur](development/architecture.md) — wie Monorepo und Backend zusammenpassen
- [Mitwirken](development/contributing.md) — das Repository für die lokale Entwicklung einrichten
