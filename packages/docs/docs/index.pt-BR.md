# Visão geral

**Anote AI** é um assistente de codificação com IA unificado e uma plataforma de chat privada. Ele lê seu codebase, edita arquivos, executa comandos, revisa pull requests e responde perguntas sobre seus documentos — disponível no terminal, na IDE, no navegador, no aplicativo desktop e no celular.

## Começando

O Anote funciona em várias superfícies: CLI, VS Code, web, desktop e mobile. Escolha uma abaixo para começar. A maioria das superfícies se comunica com o backend hospedado do Anote ou com sua própria instância auto-hospedada (veja [Configuração](getting-started/configuration.md)).

=== "CLI"

    A CLI completa para trabalhar com o Anote diretamente no seu terminal. Faça perguntas, corrija bugs, revise pull requests e pesquise seu codebase sem sair do shell.

    ```bash
    npm install -g @anote-ai/anote
    ```

    Requer Node.js 18 ou superior. Depois, em qualquer projeto:

    ```bash
    cd your-project
    anote init
    anote ask "explain this codebase"
    ```

    O `anote init` guia você na configuração da sua chave de API e do provedor de LLM preferido.

    [Continuar com o Guia rápido →](getting-started/quickstart.md)

=== "VS Code"

    A extensão do VS Code traz uma barra lateral de chat, revisão de diff inline e respostas em streaming diretamente para o seu editor.

    Procure por **"Anote"** no marketplace de extensões do VS Code, ou instale via:

    ```bash
    code --install-extension anote-ai.anote-ai-coding
    ```

    [Visão geral da extensão VS Code →](vscode/overview.md)

=== "Aplicativo Web"

    Uma interface de chat no navegador ao estilo ChatGPT, com upload de documentos e perguntas e respostas baseadas em RAG. Hospede você mesmo com Docker Compose:

    ```bash
    git clone https://github.com/anote-ai/Panacea
    cd Panacea
    cp packages/backend/.env.example packages/backend/.env
    # Edite o .env com suas chaves de API
    docker compose up
    ```

    Frontend: `http://localhost:3000` · Backend: `http://localhost:5000`

    [Visão geral do aplicativo Web →](web/overview.md)

=== "Desktop"

    Um aplicativo Electron privado e capaz de funcionar offline. Todos os dados permanecem na sua máquina, e funciona com modelos Ollama locais quando você não quiser depender de um provedor hospedado.

    Baixe a versão mais recente em [GitHub Releases](https://github.com/anote-ai/Panacea/releases) — disponível para **macOS** (DMG), **Windows** (instalador) e **Linux** (AppImage/DEB/RPM).

    [Visão geral do aplicativo Desktop →](desktop/overview.md)

=== "Mobile"

    Um cliente de chat nativo para iOS e Android, construído com Expo.

    ```bash
    cd packages/mobile
    npm install
    npx expo start
    ```

    Escaneie o código QR com o aplicativo Expo Go, ou execute em um simulador.

    [Visão geral do aplicativo Mobile →](mobile/overview.md)

## O que você pode fazer

??? abstract "Fazer perguntas sobre seu codebase"

    ```bash
    anote ask "how does the authentication middleware work?"
    anote ask --file src/auth.ts "explain this file"
    anote ask --compare               # comparação lado a lado entre vários modelos
    cat src/handler.py | anote ask "what could go wrong here?"
    ```

??? bug "Corrigir bugs automaticamente"

    O `anote fix --loop` itera sobre sua suíte de testes — até `--max-iterations` rodadas — até passar, ou corrige um único arquivo com `--file`.

    ```bash
    anote fix --loop --max-iterations 5
    ```

??? example "Revisar pull requests"

    ```bash
    anote review --pr 42
    ```

    Revisões de bugs, problemas de segurança e qualidade — localmente em um diretório/arquivo, ou publicadas diretamente em um PR do GitHub.

??? search "Pesquisar seu codebase semanticamente"

    ```bash
    anote index              # construir um índice TF-IDF (uma vez, depois mantido atualizado)
    anote search "JWT token validation"
    ```

??? question "Conversar e tirar dúvidas sobre seus documentos"

    Envie documentos no [Aplicativo Web](web/overview.md) ou no [Aplicativo Desktop](desktop/overview.md) e faça perguntas sobre eles — baseado em RAG via `POST /api/documents/{id}/ask`.

??? tip "Auditar segurança e performance"

    ```bash
    anote security --severity high --fix
    anote perf --focus "database,bundle" --fix
    ```

??? note "Gerar changelogs e documentação, ou executar migrações"

    ```bash
    anote changelog --since v1.2.0
    anote docs src/api.ts --style jsdoc
    anote migrate --from "React 17" --to "React 18"
    ```

??? info "Verificar sua configuração"

    ```bash
    anote doctor
    ```

    Verifica Node.js ≥ 18, `ANTHROPIC_API_KEY`, `.anote.json`, `CLAW.md` e git.

## Use o Anote em qualquer lugar

| Eu quero... | Melhor opção |
|---|---|
| Trabalhar pelo meu terminal | [CLI](cli/overview.md) |
| Ajuda de IA diretamente no meu editor | [Extensão VS Code](vscode/overview.md) |
| Conversar com documentos no navegador | [Aplicativo Web](web/overview.md) |
| Manter tudo privado e offline | [Aplicativo Desktop](desktop/overview.md) — funciona com modelos Ollama locais |
| Conversar pelo celular | [Aplicativo Mobile](mobile/overview.md) |
| Chamar o Anote a partir do meu próprio código ou scripts | [SDK TypeScript](sdk/typescript.md) ou [SDK Python](sdk/python.md) |
| Integrar diretamente com a API REST | [API do Backend](api/overview.md) |
| Automatizar revisão de PR ou verificações de CI | [CLI: `anote review --pr`](cli/commands.md#anote-review) |

## Provedores de LLM suportados

- **Anthropic** — Claude (`claude-opus-4-8`, `claude-sonnet-4-6`, `claude-haiku-4-5`)
- **OpenAI** — GPT-4o, GPT-4o-mini
- **Google** — Gemini 2.0 Flash, Gemini 1.5 Pro
- **Ollama** — qualquer modelo local (Llama 3, Mistral, etc.)
- **xAI** — Grok

## Próximos passos

- [Guia rápido](getting-started/quickstart.md) — init, ask, fix, index, review e changelog em ordem
- [Como o Panacea funciona](core-concepts/how-it-works.md) — o loop agêntico, ferramentas e streaming
- [Modos de permissão](use-panacea/permission-modes.md) — controle o que o agente pode fazer sem perguntar
- [Fluxos de trabalho comuns](use-panacea/common-workflows.md) — padrões passo a passo para tarefas do dia a dia
- [Configuração](getting-started/configuration.md) — chaves de API, configuração do provedor e `~/.anote/config.json`
- [Comandos CLI](cli/commands.md) — a referência completa de comandos
- [API do Backend](api/overview.md) — os endpoints REST que alimentam cada superfície
- [Arquitetura](development/architecture.md) — como o monorepo e o backend se encaixam
- [Contribuindo](development/contributing.md) — configure o repositório para desenvolvimento local
