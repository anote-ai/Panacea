# Aperçu

**Anote AI** est un assistant de codage IA unifié et une plateforme de chat privée. Il lit votre codebase, modifie des fichiers, exécute des commandes, révise les pull requests et répond à des questions sur vos documents — disponible dans votre terminal, votre IDE, votre navigateur, votre application de bureau et votre téléphone.

## Commencer

Anote fonctionne sur plusieurs surfaces : le CLI, VS Code, le web, le bureau et le mobile. Choisissez-en une ci-dessous pour démarrer. La plupart des surfaces communiquent avec le backend Anote hébergé ou votre propre instance auto-hébergée (voir [Configuration](getting-started/configuration.md)).

=== "CLI"

    Le CLI complet pour travailler avec Anote directement dans votre terminal. Posez des questions, corrigez des bugs, révisez des pull requests et recherchez dans votre codebase sans quitter le shell.

    ```bash
    npm install -g @anote-ai/anote
    ```

    Nécessite Node.js 18 ou une version ultérieure. Puis, dans n'importe quel projet :

    ```bash
    cd your-project
    anote init
    anote ask "explain this codebase"
    ```

    `anote init` vous guide pour configurer votre clé API et votre fournisseur de LLM préféré.

    [Continuer avec le Démarrage rapide →](getting-started/quickstart.md)

=== "VS Code"

    L'extension VS Code apporte une barre latérale de chat, une révision de diff en ligne et des réponses en streaming directement dans votre éditeur.

    Recherchez **« Anote »** dans la marketplace des extensions VS Code, ou installez via :

    ```bash
    code --install-extension anote-ai.anote-ai-coding
    ```

    [Aperçu de l'extension VS Code →](vscode/overview.md)

=== "Application Web"

    Une interface de chat façon ChatGPT dans le navigateur, avec téléversement de documents et questions-réponses basées sur du RAG. Auto-hébergez-la avec Docker Compose :

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

    Une application Electron privée, utilisable hors ligne. Toutes les données restent sur votre machine, et elle fonctionne avec des modèles Ollama locaux lorsque vous ne voulez pas faire appel à un fournisseur hébergé.

    Téléchargez la dernière version depuis [GitHub Releases](https://github.com/anote-ai/Panacea/releases) — disponible pour **macOS** (DMG), **Windows** (installateur) et **Linux** (AppImage/DEB/RPM).

    [Aperçu de l'application Bureau →](desktop/overview.md)

=== "Mobile"

    Un client de chat natif iOS et Android construit avec Expo.

    ```bash
    cd packages/mobile
    npm install
    npx expo start
    ```

    Scannez le QR code avec l'application Expo Go, ou lancez-le dans un simulateur.

    [Aperçu de l'application Mobile →](mobile/overview.md)

## Ce que vous pouvez faire

??? abstract "Poser des questions sur votre codebase"

    ```bash
    anote ask "how does the authentication middleware work?"
    anote ask --file src/auth.ts "explain this file"
    anote ask --compare               # comparaison côte à côte entre plusieurs modèles
    cat src/handler.py | anote ask "what could go wrong here?"
    ```

??? bug "Corriger des bugs automatiquement"

    `anote fix --loop` itère sur votre suite de tests — jusqu'à `--max-iterations` fois — jusqu'à ce qu'elle passe, ou corrige un seul fichier avec `--file`.

    ```bash
    anote fix --loop --max-iterations 5
    ```

??? example "Réviser des pull requests"

    ```bash
    anote review --pr 42
    ```

    Révisions pour les bugs, les problèmes de sécurité et la qualité — localement sur un dossier/fichier, ou publiées directement sur une PR GitHub.

??? search "Rechercher dans votre codebase sémantiquement"

    ```bash
    anote index              # construire un index TF-IDF (une fois, puis maintenu à jour)
    anote search "JWT token validation"
    ```

??? question "Discuter et poser des questions sur vos documents"

    Téléversez des documents dans l'[application Web](web/overview.md) ou l'[application Bureau](desktop/overview.md) et posez-leur des questions — basé sur du RAG via `POST /api/documents/{id}/ask`.

??? tip "Auditer la sécurité et les performances"

    ```bash
    anote security --severity high --fix
    anote perf --focus "database,bundle" --fix
    ```

??? note "Générer des changelogs et de la documentation, ou effectuer des migrations"

    ```bash
    anote changelog --since v1.2.0
    anote docs src/api.ts --style jsdoc
    anote migrate --from "React 17" --to "React 18"
    ```

??? info "Vérifier votre configuration"

    ```bash
    anote doctor
    ```

    Vérifie Node.js ≥ 18, `ANTHROPIC_API_KEY`, `.anote.json`, `CLAW.md`, et git.

## Utiliser Anote partout

| Je veux... | Meilleure option |
|---|---|
| Travailler depuis mon terminal | [CLI](cli/overview.md) |
| Obtenir de l'aide IA directement dans mon éditeur | [Extension VS Code](vscode/overview.md) |
| Discuter avec des documents dans un navigateur | [Application Web](web/overview.md) |
| Tout garder privé et hors ligne | [Application Bureau](desktop/overview.md) — fonctionne avec des modèles Ollama locaux |
| Discuter depuis mon téléphone | [Application Mobile](mobile/overview.md) |
| Appeler Anote depuis mon propre code ou mes scripts | [SDK TypeScript](sdk/typescript.md) ou [SDK Python](sdk/python.md) |
| M'intégrer directement à l'API REST | [API Backend](api/overview.md) |
| Automatiser la révision de PR ou les vérifications CI | [CLI : `anote review --pr`](cli/commands.md#anote-review) |

## Fournisseurs de LLM pris en charge

- **Anthropic** — Claude (`claude-opus-4-8`, `claude-sonnet-4-6`, `claude-haiku-4-5`)
- **OpenAI** — GPT-4o, GPT-4o-mini
- **Google** — Gemini 2.0 Flash, Gemini 1.5 Pro
- **Ollama** — tout modèle local (Llama 3, Mistral, etc.)
- **xAI** — Grok

## Prochaines étapes

- [Démarrage rapide](getting-started/quickstart.md) — init, ask, fix, index, review et changelog dans l'ordre
- [Comment fonctionne Panacea](core-concepts/how-it-works.md) — la boucle agentique, les outils et le streaming
- [Modes de permission](use-panacea/permission-modes.md) — contrôlez ce que l'agent peut faire sans demander
- [Workflows courants](use-panacea/common-workflows.md) — des schémas étape par étape pour les tâches quotidiennes
- [Configuration](getting-started/configuration.md) — clés API, configuration du fournisseur, et `~/.anote/config.json`
- [Commandes CLI](cli/commands.md) — la référence complète des commandes
- [API Backend](api/overview.md) — les endpoints REST qui alimentent toutes les surfaces
- [Architecture](development/architecture.md) — comment le monorepo et le backend s'assemblent
- [Contribuer](development/contributing.md) — configurer le dépôt pour le développement local
