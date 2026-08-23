# Explore o Diretório .anote

O CLI da Panacea lê a configuração de dois lugares: um arquivo por projeto e um global.

## Configuração do projeto

A Panacea procura para cima a partir do seu diretório atual pelo primeiro arquivo que encontrar, nesta ordem:

- `.anote.json`
- `.claw.json`
- `anote.config.json`

```json
{
  "model": "claude-sonnet-4-6",
  "permissionMode": "default",
  "maxTurns": 20,
  "compactAfterMessages": 40,
  "hooks": {
    "preToolUse": [],
    "postToolUse": []
  }
}
```

| Chave | Propósito |
|---|---|
| `model` | Modelo padrão para este projeto |
| `permissionMode` | `default`, `acceptEdits` ou `bypassPermissions` — veja [Modos de permissão](../use-panacea/permission-modes.md) |
| `provider` | Substituição explícita do provedor (geralmente detectado automaticamente a partir de `model`) |
| `baseUrl` | URL base para endpoints compatíveis com OpenAI, por exemplo, `http://localhost:11434/v1` para Ollama |
| `maxTurns` | Limite de turnos por sessão |
| `compactAfterMessages` | Quando compactar o histórico da sessão |
| `hooks` | Ganchos de shell `preToolUse` / `postToolUse` — veja [Estender a Panacea](extend.md) |

`anote init` cria `.anote.json` para você. `anote config` lê e escreve nele:

```bash
anote config              # mostra a configuração efetiva (global + local)
anote config get model
anote config set model gpt-4.1
anote config path         # imprime o caminho do arquivo de configuração global
anote config edit         # abre a configuração global no $EDITOR
```

## Configuração global

`~/.anote/config.json` contém seus padrões — aplicados sempre que um projeto não os substituir. A configuração do projeto sempre prevalece sobre a configuração global.

## CLAW.md

Não é JSON — um arquivo markdown que o agente lê para o contexto do projeto no início de cada sessão. Veja [Estender a Panacea](extend.md) para o que deve ser incluído.

## Próximos passos

- [Modos de permissão](../use-panacea/permission-modes.md)
- [Gerenciar sessões](../use-panacea/sessions.md)
