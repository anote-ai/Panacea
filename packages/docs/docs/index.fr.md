# Vue d'ensemble

**Anote AI** est une plateforme unifiée d'assistant de codage IA et de chatbot privé. Il lit votre code, modifie des fichiers, exécute des commandes, examine des PRs et répond à des questions sur vos documents — disponible dans votre terminal, IDE, navigateur, application de bureau et téléphone.

## Commencer

Anote fonctionne sur plusieurs surfaces : le CLI, VS Code, le web, le bureau et mobile. Choisissez-en une ci-dessous pour commencer. La plupart des surfaces communiquent avec le backend Anote hébergé ou votre propre instance auto-hébergée (voir [Configuration](getting-started/configuration.md)).

=== "CLI"

    Le CLI complet pour travailler avec Anote directement dans votre terminal. Posez des questions, corrigez des bugs, examinez des PRs et recherchez dans votre code sans quitter le shell.

    ```bash
    npm install -g @anote-ai/anote
    ```

    Nécessite Node.js 18 ou version ultérieure. Ensuite, dans n'importe quel projet :

    ```bash
    cd your-project
    anote init
    anote ask "explain this codebase"
    ```

    `anote init` vous guide pour configurer votre clé API et votre fournisseur LLM préféré.

    [Continuez avec le Démarrage Rapide →](getting-started/quickstart.md)

=== "VS Code"

    L'extension VS Code apporte une barre latérale de chat, une révision de diff en ligne et des réponses en streaming directement dans votre éditeur.

    Recherchez **"Anote"** dans le marché des extensions VS Code, ou installez via :

    ```bash
    code --install-extension anote-ai.anote-ai-coding
    ```

    [Aperçu de l'extension VS Code →](vscode/overview.md)

=== "Application Web"

    Une interface de chat de navigateur de style ChatGPT avec téléchargement de documents et Q&R soutenue par RAG. Auto-hébergez-la avec Docker Compose :

    ```bash
    git clone https://github.com/anote-ai/Panacea
    cd Panacea
    cp packages/backend/.env.example packages/backend/.env
    # Modifiez .env avec vos clés API
    docker compose up
    ```

    Frontend : `http://localhost:3000` · Backend : `http://localhost:5000`

    [Aperçu de l'application Web →](web/overview.md)

=== "Bureau"

    Une application Electron privée, capable de fonctionner hors ligne. Toutes les données restent sur votre machine, et elle fonctionne avec des modèles Ollama locaux lorsque vous ne souhaitez pas faire appel à un fournisseur hébergé.

    Téléchargez la dernière version depuis [GitHub Releases](https://github.com/anote-ai/Panacea/releases) — disponible pour **macOS** (DMG), **Windows** (installeur) et **Linux** (AppImage/DEB/RPM).

    [Aperçu de l'application de bureau →](desktop/overview.md)

=== "Mobile"

    Un client de chat natif iOS et Android construit avec Expo.

    ```bash
    cd packages/mobile
    npm install
    npx expo start
    ```

    Scannez le code QR avec l'application Expo Go, ou exécutez dans un simulateur.

    [Aperçu de l'application mobile →](mobile/overview.md)

## Ce que vous pouvez faire

??? abstract "Posez des questions sur votre code"

    ```bash
    anote ask "how does the authentication middleware work?"
    anote ask --file src/auth.ts "explain this file"
    anote ask --compare               # côte à côte sur plusieurs modèles
    cat src/handler.py | anote ask "what could go wrong here?"
    ```

??? bug "Corrigez des bugs automatiquement"

    `anote fix --loop` itère contre votre suite de tests — jusqu'à `--max-iterations` tours — jusqu'à ce qu'elle réussisse, ou corrige un seul fichier avec `--file`.

    ```bash
    anote fix --loop --max-iterations 5
    ```

??? example "Examinez les demandes de tirage"

    ```bash
    anote review --pr 42
    ```

    Examine les bugs, les problèmes de sécurité et la qualité — localement contre un répertoire/fichier, ou directement dans une PR GitHub.

??? search "Recherchez dans votre code de manière sémantique"

    ```bash
    anote index              # construisez un index TF-IDF (exécutez une fois, puis maintenez à jour)
    anote search "JWT token validation"
    ```

??? question "Discutez et posez des questions sur vos documents"

    Téléchargez des documents dans l'[Application Web](web/overview.md) ou l'[Application de Bureau](desktop/overview.md) et posez des questions à leur sujet — soutenu par RAG via `POST /api/documents/{id}/ask`.

??? tip "Auditez pour des problèmes de sécurité et de performance"

    ```bash
    anote security --severity high --fix
    anote perf --focus "database,bundle" --fix
    ```

??? note "Générez des journaux de modifications et des docs, ou exécutez des migrations"

    ```bash
    anote changelog --since v1.2.0
    anote docs src/api.ts --style jsdoc
    anote migrate --from "React 17" --to "React 18"
    ```

??? info "Vérifiez votre configuration"

    ```bash
    anote doctor
    ```

    Vérifie Node.js ≥ 18, `ANTHROPIC_API_KEY`, `.anote.json`, `CLAW.md`, et git.

## Utilisez Anote partout

| Je veux... | Meilleure option |
|---|---|
| Travailler depuis mon terminal | [CLI](cli/overview.md) |
| Obtenir de l'aide IA en ligne dans mon éditeur | [Extension VS Code](vscode/overview.md) |
| Discuter avec des documents dans un navigateur | [Application Web](web/overview.md) |
| Garder tout privé et hors ligne | [Application de Bureau](desktop/overview.md) — fonctionne avec des modèles Ollama locaux |
| Discuter depuis mon téléphone | [Application Mobile](mobile/overview.md) |
| Appeler Anote depuis mon propre code ou scripts | [SDK TypeScript](sdk/typescript.md) ou [SDK Python](sdk/python.md) |
| Intégrer directement contre l'API REST | [API Backend](api/overview.md) |
| Automatiser l'examen des PR ou les vérifications CI | [CLI : `anote review --pr`](cli/commands.md#anote-review) |

## Fournisseurs LLM pris en charge

- **Anthropic** — Claude (`claude-opus-4-8`, `claude-sonnet-4-6`, `claude-haiku-4-5`)
- **OpenAI** — GPT-4o, GPT-4o-mini
- **Google** — Gemini 2.0 Flash, Gemini 1.5 Pro
- **Ollama** — tout modèle local (Llama 3, Mistral, etc.)
- **xAI** — Grok

## Étapes suivantes

- [Démarrage Rapide](getting-started/quickstart.md) — init, ask, fix, index, review, et changelog dans l'ordre
- [Comment Panacea fonctionne](core-concepts/how-it-works.md) — la boucle agentique, les outils et le streaming
- [Modes de Permission](use-panacea/permission-modes.md) — contrôlez ce que l'agent peut faire sans demander
- [Flux de Travail Communs](use-panacea/common-workflows.md) — modèles étape par étape pour les tâches quotidiennes
- [Configuration](getting-started/configuration.md) — clés API, configuration du fournisseur, et `~/.anote/config.json`
- [Commandes CLI](cli/commands.md) — la référence complète des commandes
- [API Backend](api/overview.md) — les points de terminaison REST alimentant chaque surface
- [Architecture](development/architecture.md) — comment le monorepo et le backend s'intègrent
- [Contribuer](development/contributing.md) — configurez le dépôt pour le développement local
