# Panoramica

**Anote AI** è un assistente alla codifica AI unificato e una piattaforma di chatbot privata. Legge il tuo codice sorgente, modifica file, esegue comandi, rivede PR e risponde a domande sui tuoi documenti — disponibile nel tuo terminale, IDE, browser, app desktop e telefono.

## Iniziare

Anote funziona su diverse superfici: il CLI, VS Code, il web, desktop e mobile. Scegli una delle opzioni qui sotto per iniziare. La maggior parte delle superfici comunica con il backend Anote ospitato o la tua istanza auto-ospitata (vedi [Configurazione](getting-started/configuration.md)).

=== "CLI"

    Il CLI completo per lavorare con Anote direttamente nel tuo terminale. Fai domande, risolvi bug, rivedi PR e cerca nel tuo codice sorgente senza lasciare la shell.

    ```bash
    npm install -g @anote-ai/anote
    ```

    Richiede Node.js 18 o versioni successive. Poi, in qualsiasi progetto:

    ```bash
    cd your-project
    anote init
    anote ask "spiega questo codice sorgente"
    ```

    `anote init` ti guida nella configurazione della tua chiave API e del fornitore LLM preferito.

    [Continua con il Quick Start →](getting-started/quickstart.md)

=== "VS Code"

    L'estensione di VS Code porta una barra laterale di chat, revisione delle differenze in linea e risposte in streaming direttamente nel tuo editor.

    Cerca **"Anote"** nel marketplace delle estensioni di VS Code, oppure installa tramite:

    ```bash
    code --install-extension anote-ai.anote-ai-coding
    ```

    [Panoramica dell'estensione VS Code →](vscode/overview.md)

=== "Web App"

    Un'interfaccia di chat nel browser in stile ChatGPT con upload di documenti e Q&A supportato da RAG. Auto-ospitato con Docker Compose:

    ```bash
    git clone https://github.com/anote-ai/Panacea
    cd Panacea
    cp packages/backend/.env.example packages/backend/.env
    # Modifica .env con le tue chiavi API
    docker compose up
    ```

    Frontend: `http://localhost:3000` · Backend: `http://localhost:5000`

    [Panoramica della Web App →](web/overview.md)

=== "Desktop"

    Un'app Electron privata e in grado di funzionare offline. Tutti i dati rimangono sul tuo computer e funziona con modelli Ollama locali quando non vuoi contattare un fornitore ospitato.

    Scarica l'ultima versione da [GitHub Releases](https://github.com/anote-ai/Panacea/releases) — disponibile per **macOS** (DMG), **Windows** (installer) e **Linux** (AppImage/DEB/RPM).

    [Panoramica dell'app Desktop →](desktop/overview.md)

=== "Mobile"

    Un client di chat nativo per iOS e Android costruito con Expo.

    ```bash
    cd packages/mobile
    npm install
    npx expo start
    ```

    Scansiona il codice QR con l'app Expo Go, oppure esegui in un simulatore.

    [Panoramica dell'app Mobile →](mobile/overview.md)

## Cosa puoi fare

??? abstract "Fai domande sul tuo codice sorgente"

    ```bash
    anote ask "come funziona il middleware di autenticazione?"
    anote ask --file src/auth.ts "spiega questo file"
    anote ask --compare               # affianca più modelli
    cat src/handler.py | anote ask "cosa potrebbe andare storto qui?"
    ```

??? bug "Correggi bug automaticamente"

    `anote fix --loop` itera contro il tuo suite di test — fino a `--max-iterations` round — finché non passa, o corregge un singolo file con `--file`.

    ```bash
    anote fix --loop --max-iterations 5
    ```

??? example "Rivedi le pull request"

    ```bash
    anote review --pr 42
    ```

    Rivede per bug, problemi di sicurezza e qualità — localmente contro una directory/file, o pubblicato direttamente su una PR di GitHub.

??? search "Cerca nel tuo codice sorgente semanticamente"

    ```bash
    anote index              # costruisci un indice TF-IDF (esegui una volta, poi mantienilo aggiornato)
    anote search "validazione del token JWT"
    ```

??? question "Chat e Q&A sui tuoi documenti"

    Carica documenti nell'[Web App](web/overview.md) o nell'[App Desktop](desktop/overview.md) e fai domande su di essi — supportato da RAG tramite `POST /api/documents/{id}/ask`.

??? tip "Audita per problemi di sicurezza e prestazioni"

    ```bash
    anote security --severity high --fix
    anote perf --focus "database,bundle" --fix
    ```

??? note "Genera changelog e documenti, o esegui migrazioni"

    ```bash
    anote changelog --since v1.2.0
    anote docs src/api.ts --style jsdoc
    anote migrate --from "React 17" --to "React 18"
    ```

??? info "Controlla la tua configurazione"

    ```bash
    anote doctor
    ```

    Controlla Node.js ≥ 18, `ANTHROPIC_API_KEY`, `.anote.json`, `CLAW.md` e git.

## Usa Anote ovunque

| Voglio... | Migliore opzione |
|---|---|
| Lavorare dal mio terminale | [CLI](cli/overview.md) |
| Ottenere aiuto AI in linea nel mio editor | [Estensione VS Code](vscode/overview.md) |
| Chattare con documenti in un browser | [Web App](web/overview.md) |
| Tenere tutto privato e offline | [App Desktop](desktop/overview.md) — funziona con modelli Ollama locali |
| Chattare dal mio telefono | [App Mobile](mobile/overview.md) |
| Chiamare Anote dal mio codice o script | [TypeScript SDK](sdk/typescript.md) o [Python SDK](sdk/python.md) |
| Integrare direttamente contro l'API REST | [Backend API](api/overview.md) |
| Automatizzare la revisione delle PR o i controlli CI | [CLI: `anote review --pr`](cli/commands.md#anote-review) |

## Fornitori LLM supportati

- **Anthropic** — Claude (`claude-opus-4-8`, `claude-sonnet-4-6`, `claude-haiku-4-5`)
- **OpenAI** — GPT-4o, GPT-4o-mini
- **Google** — Gemini 2.0 Flash, Gemini 1.5 Pro
- **Ollama** — qualsiasi modello locale (Llama 3, Mistral, ecc.)
- **xAI** — Grok

## Prossimi passi

- [Quick Start](getting-started/quickstart.md) — init, ask, fix, index, review e changelog in ordine
- [Come funziona Panacea](core-concepts/how-it-works.md) — il ciclo agentico, strumenti e streaming
- [Modalità di autorizzazione](use-panacea/permission-modes.md) — controlla cosa può fare l'agente senza chiedere
- [Flussi di lavoro comuni](use-panacea/common-workflows.md) — modelli passo-passo per compiti quotidiani
- [Configurazione](getting-started/configuration.md) — chiavi API, configurazione del fornitore e `~/.anote/config.json`
- [Comandi CLI](cli/commands.md) — il riferimento completo ai comandi
- [Backend API](api/overview.md) — gli endpoint REST che alimentano ogni superficie
- [Architettura](development/architecture.md) — come il monorepo e il backend si integrano
- [Contribuire](development/contributing.md) — configura il repo per lo sviluppo locale
