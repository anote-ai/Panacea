# Panoramica

**Anote AI** è un assistente di coding IA unificato e una piattaforma di chat privata. Legge la tua codebase, modifica file, esegue comandi, revisiona pull request e risponde a domande sui tuoi documenti — disponibile nel terminale, nell'IDE, nel browser, nell'app desktop e sul telefono.

## Per iniziare

Anote funziona su più superfici: CLI, VS Code, web, desktop e mobile. Scegline una qui sotto per iniziare. La maggior parte delle superfici comunica con il backend Anote ospitato o con la tua istanza self-hosted (vedi [Configurazione](getting-started/configuration.md)).

=== "CLI"

    La CLI completa per lavorare con Anote direttamente nel terminale. Fai domande, correggi bug, revisiona pull request e cerca nella tua codebase senza uscire dalla shell.

    ```bash
    npm install -g @anote-ai/anote
    ```

    Richiede Node.js 18 o successivo. Poi, in qualsiasi progetto:

    ```bash
    cd your-project
    anote init
    anote ask "explain this codebase"
    ```

    `anote init` ti guida nell'impostazione della tua chiave API e del provider LLM preferito.

    [Continua con la Guida rapida →](getting-started/quickstart.md)

=== "VS Code"

    L'estensione VS Code porta una barra laterale di chat, revisione diff inline e risposte in streaming direttamente nel tuo editor.

    Cerca **"Anote"** nel marketplace delle estensioni VS Code, oppure installa con:

    ```bash
    code --install-extension anote-ai.anote-ai-coding
    ```

    [Panoramica dell'estensione VS Code →](vscode/overview.md)

=== "App Web"

    Un'interfaccia di chat in stile ChatGPT nel browser, con caricamento documenti e Q&A basate su RAG. Self-hosting con Docker Compose:

    ```bash
    git clone https://github.com/anote-ai/Panacea
    cd Panacea
    cp packages/backend/.env.example packages/backend/.env
    # Modifica .env con le tue chiavi API
    docker compose up
    ```

    Frontend: `http://localhost:3000` · Backend: `http://localhost:5000`

    [Panoramica dell'app Web →](web/overview.md)

=== "Desktop"

    Un'app Electron privata e utilizzabile offline. Tutti i dati restano sul tuo computer, e funziona con modelli Ollama locali quando non vuoi rivolgerti a un provider ospitato.

    Scarica l'ultima versione da [GitHub Releases](https://github.com/anote-ai/Panacea/releases) — disponibile per **macOS** (DMG), **Windows** (installer) e **Linux** (AppImage/DEB/RPM).

    [Panoramica dell'app Desktop →](desktop/overview.md)

=== "Mobile"

    Un client di chat nativo per iOS e Android, costruito con Expo.

    ```bash
    cd packages/mobile
    npm install
    npx expo start
    ```

    Scansiona il codice QR con l'app Expo Go, oppure eseguilo in un simulatore.

    [Panoramica dell'app Mobile →](mobile/overview.md)

## Cosa puoi fare

??? abstract "Fare domande sulla tua codebase"

    ```bash
    anote ask "how does the authentication middleware work?"
    anote ask --file src/auth.ts "explain this file"
    anote ask --compare               # confronto affiancato tra più modelli
    cat src/handler.py | anote ask "what could go wrong here?"
    ```

??? bug "Correggere bug automaticamente"

    `anote fix --loop` itera sulla tua suite di test — fino a `--max-iterations` cicli — finché non passa, oppure corregge un singolo file con `--file`.

    ```bash
    anote fix --loop --max-iterations 5
    ```

??? example "Revisionare pull request"

    ```bash
    anote review --pr 42
    ```

    Revisioni per bug, problemi di sicurezza e qualità — localmente su una cartella/file, oppure pubblicate direttamente su una PR GitHub.

??? search "Cercare nella tua codebase semanticamente"

    ```bash
    anote index              # crea un indice TF-IDF (una volta, poi mantenuto aggiornato)
    anote search "JWT token validation"
    ```

??? question "Chattare e fare domande sui tuoi documenti"

    Carica documenti nell'[app Web](web/overview.md) o nell'[app Desktop](desktop/overview.md) e fai domande su di essi — basato su RAG tramite `POST /api/documents/{id}/ask`.

??? tip "Verificare sicurezza e prestazioni"

    ```bash
    anote security --severity high --fix
    anote perf --focus "database,bundle" --fix
    ```

??? note "Generare changelog e documentazione, o eseguire migrazioni"

    ```bash
    anote changelog --since v1.2.0
    anote docs src/api.ts --style jsdoc
    anote migrate --from "React 17" --to "React 18"
    ```

??? info "Verificare la configurazione"

    ```bash
    anote doctor
    ```

    Verifica Node.js ≥ 18, `ANTHROPIC_API_KEY`, `.anote.json`, `CLAW.md` e git.

## Usa Anote ovunque

| Voglio... | Opzione migliore |
|---|---|
| Lavorare dal mio terminale | [CLI](cli/overview.md) |
| Aiuto IA direttamente nel mio editor | [Estensione VS Code](vscode/overview.md) |
| Chattare con documenti nel browser | [App Web](web/overview.md) |
| Tenere tutto privato e offline | [App Desktop](desktop/overview.md) — funziona con modelli Ollama locali |
| Chattare dal telefono | [App Mobile](mobile/overview.md) |
| Chiamare Anote dal mio codice o script | [SDK TypeScript](sdk/typescript.md) o [SDK Python](sdk/python.md) |
| Integrarmi direttamente con la REST API | [API Backend](api/overview.md) |
| Automatizzare la revisione PR o i controlli CI | [CLI: `anote review --pr`](cli/commands.md#anote-review) |

## Provider LLM supportati

- **Anthropic** — Claude (`claude-opus-4-8`, `claude-sonnet-4-6`, `claude-haiku-4-5`)
- **OpenAI** — GPT-4o, GPT-4o-mini
- **Google** — Gemini 2.0 Flash, Gemini 1.5 Pro
- **Ollama** — qualsiasi modello locale (Llama 3, Mistral, ecc.)
- **xAI** — Grok

## Prossimi passi

- [Guida rapida](getting-started/quickstart.md) — init, ask, fix, index, review e changelog in ordine
- [Come funziona Panacea](core-concepts/how-it-works.md) — il ciclo agentico, gli strumenti e lo streaming
- [Modalità di permesso](use-panacea/permission-modes.md) — controlla cosa può fare l'agente senza chiedere
- [Workflow comuni](use-panacea/common-workflows.md) — schemi passo-passo per le attività quotidiane
- [Configurazione](getting-started/configuration.md) — chiavi API, configurazione del provider e `~/.anote/config.json`
- [Comandi CLI](cli/commands.md) — il riferimento completo dei comandi
- [API Backend](api/overview.md) — gli endpoint REST che alimentano ogni superficie
- [Architettura](development/architecture.md) — come si integrano monorepo e backend
- [Contribuire](development/contributing.md) — configura il repository per lo sviluppo locale
