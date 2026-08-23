# Como o Panacea Funciona

O Panacea executa um **loop agente**: ele lê seu prompt, decide quais ferramentas chamar, as executa, lê os resultados e repete — transmitindo seu raciocínio e edições de volta para você — até que a tarefa esteja concluída ou atinja um limite de turnos.

## As ferramentas

Por padrão, o agente do Panacea pode chamar:

| Ferramenta | Propósito |
|---|---|
| `Read` | Ler um arquivo |
| `Write` | Criar ou sobrescrever um arquivo |
| `Edit` | Fazer uma alteração direcionada em um arquivo |
| `Bash` | Executar um comando de shell |
| `Glob` | Encontrar arquivos por padrão |
| `Grep` | Pesquisar conteúdos de arquivos |

Alguns comandos restringem essa lista — `anote review` e `anote diff`, por exemplo, permitem apenas `Read`, `Glob`, `Grep` e `Bash`, já que uma revisão não deve escrever arquivos.

## Turnos e compactação

Cada par de chamada/resposta de ferramenta conta como um turno. O agente para após `maxTurns` (padrão 30, configurável via `anote config set maxTurns <n>` ou `.anote.json`). Sessões longas são compactadas após `compactAfterMessages` (padrão 40) para manter a janela de contexto gerenciável.

## Streaming

Cada interface — CLI, VS Code, Web, Desktop — se comunica com o mesmo endpoint de backend (`POST /api/chat/stream`), que transmite a resposta do modelo e a atividade da ferramenta via SSE à medida que acontece. Você vê leituras de arquivos, edições e saídas de comandos ao vivo, não apenas a resposta final.

## Multi-fornecedor

O loop do agente não está vinculado a um único modelo. `anote ask --compare` executa o mesmo prompt em vários modelos lado a lado, e `--model` na maioria dos comandos aceita qualquer fornecedor configurado (`claude-sonnet-4-6`, `gpt-4.1`, `gemini-2.5-pro`, ou um `ollama/<model>` local).

## Próximos passos

- [Modos de permissão](../use-panacea/permission-modes.md) — controle se o agente pergunta antes de editar ou executar comandos
- [Expandir o Panacea](extend.md) — CLAW.md e hooks
- [Comandos CLI](../cli/commands.md) — a referência completa de comandos
