# Biblioteca de Prompts

Copie e cole prompts para `anote ask`, `anote chat` e `anote fix`, organizados por tarefa.

## Compreendendo o código

```bash
anote ask "o que este código faz, em um nível alto?"
anote ask --file src/payments/webhook.ts "explique este arquivo linha por linha"
anote ask "onde o limitador de taxa está configurado e quais são os limites?"
anote ask "o que quebraria se eu removesse a camada de cache aqui?"
```

## Depuração

```bash
anote fix --error "$(cat error.log)"
anote ask "por que este teste falha intermitentemente, mas não consistentemente?"
anote fix src/db/pool.ts "as conexões não estão sendo devolvidas ao pool"
```

## Revisão de código

```bash
anote review --file src/auth/session.ts
anote review --pr 42
anote diff --staged -c "focar no tratamento de erros e casos extremos"
```

## Refatoração

```bash
anote refactor src/utils.ts "divida isso em funções menores e de único propósito" --dry-run
anote ask "existe uma maneira mais simples de expressar essa lógica?" --file src/parser.ts
anote migrate --from "moment" --to "date-fns"
```

## Escrevendo testes

```bash
anote test src/utils/validate.ts --coverage --write
anote ask "quais casos extremos estou perdendo para esta função?" --file src/utils/validate.ts
```

## Segurança e desempenho

```bash
anote security --severity high
anote perf --focus "banco de dados,tamanho do pacote"
```

## Documentação

```bash
anote docs src/api/client.ts --style jsdoc
anote changelog --since v1.2.0
anote explain --stdout                       # resumo rápido da arquitetura
```

## Próximos passos

- [Fluxos de trabalho comuns](common-workflows.md)
- [Comandos CLI](../cli/commands.md)
