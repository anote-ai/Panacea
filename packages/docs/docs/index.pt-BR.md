# Visão Geral

**Anote AI** é uma plataforma unificada de assistente de codificação por IA e chatbot privado. Ele lê seu código, edita arquivos, executa comandos, revisa PRs e responde perguntas sobre seus documentos — disponível no seu terminal, IDE, navegador, aplicativo de desktop e telefone.

## Começando

Anote funciona em várias superfícies: o CLI, VS Code, a web, desktop e mobile. Escolha uma abaixo para começar. A maioria das superfícies se conecta ao backend hospedado do Anote ou à sua própria instância auto-hospedada (veja [Configuração](getting-started/configuration.md)).

=== "CLI"

    O CLI completo para trabalhar com Anote diretamente no seu terminal. Faça perguntas, corrija bugs, revise PRs e pesquise seu código sem sair do shell.

    ```bash
    npm install -g @anote-ai/anote
    ```

    Requer Node.js 18 ou posterior. Então, em qualquer projeto:

    ```bash
    cd seu-projeto
    anote init
    anote ask "explique este código"
    ```

    `anote init` orienta você na configuração da sua chave de API e provedor LLM preferido.

    [Continue com o Início Rápido →](getting-started/quickstart.md)

=== "VS Code"

    A extensão do VS Code traz uma barra lateral de chat, revisão de diffs inline e respostas em streaming diretamente no seu editor.

    Pesquise por **"Anote"** no marketplace de Extensões do VS Code, ou instale via:

    ```bash
    code --install-extension anote-ai.anote-ai-coding
    ```

    [Visão geral da Extensão do VS Code →](vscode/overview.md)

=== "Aplicativo Web"

    Uma interface de chat no navegador estilo ChatGPT com upload de documentos e Q&A suportado por RAG. Auto-hospede com Docker Compose:

    ```bash
    git clone https://github.com/anote-ai/Panacea
    cd Panacea
    cp packages/backend/.env.example packages/backend/.env
    # Edite .env com suas chaves de API
    docker compose up
    ```

    Frontend: `http://localhost:3000` · Backend: `http://localhost:5000`

    [Visão geral do Aplicativo Web →](web/overview.md)

=== "Desktop"

    Um aplicativo Electron privado, capaz de funcionar offline. Todos os dados permanecem na sua máquina, e ele funciona com modelos locais do Ollama quando você não deseja chamar um provedor hospedado.

    Baixe a versão mais recente do [GitHub Releases](https://github.com/anote-ai/Panacea/releases) — disponível para **macOS** (DMG), **Windows** (instalador) e **Linux** (AppImage/DEB/RPM).

    [Visão geral do Aplicativo Desktop →](desktop/overview.md)

=== "Mobile"

    Um cliente de chat nativo para iOS e Android construído com Expo.

    ```bash
    cd packages/mobile
    npm install
    npx expo start
    ```

    Escaneie o código QR com o aplicativo Expo Go, ou execute em um simulador.

    [Visão geral do Aplicativo Mobile →](mobile/overview.md)

## O que você pode fazer

??? abstract "Faça perguntas sobre seu código"

    ```bash
    anote ask "como funciona o middleware de autenticação?"
    anote ask --file src/auth.ts "explique este arquivo"
    anote ask --compare               # lado a lado entre vários modelos
    cat src/handler.py | anote ask "o que poderia dar errado aqui?"
    ```

??? bug "Corrija bugs automaticamente"

    `anote fix --loop` itera contra sua suíte de testes — até `--max-iterations` rodadas — até que passe, ou corrige um único arquivo com `--file`.

    ```bash
    anote fix --loop --max-iterations 5
    ```

??? example "Revise pull requests"

    ```bash
    anote review --pr 42
    ```

    Revisões para bugs, problemas de segurança e qualidade — localmente contra um diretório/arquivo, ou postadas diretamente em um PR do GitHub.

??? search "Pesquise seu código semanticamente"

    ```bash
    anote index              # construa um índice TF-IDF (execute uma vez, depois mantenha atualizado)
    anote search "validação de token JWT"
    ```

??? question "Converse e faça Q&A sobre seus documentos"

    Faça upload de documentos no [Aplicativo Web](web/overview.md) ou [Aplicativo Desktop](desktop/overview.md) e faça perguntas sobre eles — suportado por RAG via `POST /api/documents/{id}/ask`.

??? tip "Audite por problemas de segurança e desempenho"

    ```bash
    anote security --severity high --fix
    anote perf --focus "database,bundle" --fix
    ```

??? note "Gere changelogs e docs, ou execute migrações"

    ```bash
    anote changelog --since v1.2.0
    anote docs src/api.ts --style jsdoc
    anote migrate --from "React 17" --to "React 18"
    ```

??? info "Verifique sua configuração"

    ```bash
    anote doctor
    ```

    Verifica Node.js ≥ 18, `ANTHROPIC_API_KEY`, `.anote.json`, `CLAW.md`, e git.

## Use Anote em todos os lugares

| Eu quero... | Melhor opção |
|---|---|
| Trabalhar a partir do meu terminal | [CLI](cli/overview.md) |
| Obter ajuda de IA inline no meu editor | [Extensão do VS Code](vscode/overview.md) |
| Conversar com documentos em um navegador | [Aplicativo Web](web/overview.md) |
| Manter tudo privado e offline | [Aplicativo Desktop](desktop/overview.md) — funciona com modelos locais do Ollama |
| Conversar do meu telefone | [Aplicativo Mobile](mobile/overview.md) |
| Chamar Anote do meu próprio código ou scripts | [TypeScript SDK](sdk/typescript.md) ou [Python SDK](sdk/python.md) |
| Integrar diretamente contra a API REST | [Backend API](api/overview.md) |
| Automatizar revisão de PR ou verificações de CI | [CLI: `anote review --pr`](cli/commands.md#anote-review) |

## Provedores LLM suportados

- **Anthropic** — Claude (`claude-opus-4-8`, `claude-sonnet-4-6`, `claude-haiku-4-5`)
- **OpenAI** — GPT-4o, GPT-4o-mini
- **Google** — Gemini 2.0 Flash, Gemini 1.5 Pro
- **Ollama** — qualquer modelo local (Llama 3, Mistral, etc.)
- **xAI** — Grok

## Próximos passos

- [Início Rápido](getting-started/quickstart.md) — init, ask, fix, index, review e changelog em ordem
- [Como o Panacea Funciona](core-concepts/how-it-works.md) — o loop agente, ferramentas e streaming
- [Modos de Permissão](use-panacea/permission-modes.md) — controle o que o agente pode fazer sem perguntar
- [Fluxos de Trabalho Comuns](use-panacea/common-workflows.md) — padrões passo a passo para tarefas do dia a dia
- [Configuração](getting-started/configuration.md) — chaves de API, configuração do provedor e `~/.anote/config.json`
- [Comandos CLI](cli/commands.md) — a referência completa de comandos
- [Backend API](api/overview.md) — os endpoints REST que alimentam cada superfície
- [Arquitetura](development/architecture.md) — como o monorepo e o backend se encaixam
- [Contribuindo](development/contributing.md) — configure o repositório para desenvolvimento local
