# Modos de Permissão

Panacea possui três modos de permissão, controlando se o agente pergunta antes de escrever arquivos ou executar comandos.

| Modo | Comportamento |
|---|---|
| `default` | Confirma antes de editar arquivos ou executar comandos que não são somente leitura |
| `acceptEdits` | Aceita automaticamente edições de arquivos sem perguntar |
| `bypassPermissions` | Executa tudo sem confirmação — use com cuidado |

Defina globalmente ou por projeto:

```bash
anote config set permissionMode acceptEdits
```

ou em `.anote.json`:

```json
{ "permissionMode": "acceptEdits" }
```

## Substituições por comando

A maioria dos comandos não requer que você altere a configuração global — eles aceitam suas próprias flags para a mesma ideia:

| Flag | Disponível em | Efeito |
|---|---|---|
| `--auto` | `fix`, `refactor` | Aceita automaticamente edições apenas para esta execução |
| `--dry-run` | `fix`, `docs`, `migrate`, `security`, `perf`, `refactor`, `generate`, `changelog`, `commit`, `review` | Mostra o que aconteceria sem escrever nada |
| `--no-edit` | `ask` | Somente leitura — o agente não pode modificar arquivos mesmo que queira |
| `--yes` | `init` | Ignora prompts interativos, aceita padrões |

`anote fix --loop` implica `acceptEdits` automaticamente, já que precisa continuar editando em iterações sem parar para perguntar a cada vez.

## Hooks como uma camada de política

Para qualquer coisa mais específica do que "perguntar vs. não perguntar" — como bloquear chamadas `Bash` que tocam um determinado caminho — use um hook `preToolUse` em vez disso. Veja [Estender Panacea](../core-concepts/extend.md).

## Próximos passos

- [Como o Panacea funciona](../core-concepts/how-it-works.md) — o loop do agente que esses modos controlam
- [Explore o diretório .anote](../core-concepts/anote-directory.md) — onde `permissionMode` reside na configuração
