# Fluxos de Trabalho Comuns

Padrões passo a passo para tarefas do dia a dia com o CLI do Panacea.

## Explorar um código desconhecido

```bash
anote explain                       # gera um tour CODEBASE.md
anote explain src/auth.ts "como isso funciona?"
anote index && anote search "validação JWT"
```

`explain` sem argumentos escreve uma visão geral `CODEBASE.md` de todo o repositório. Aponte para um arquivo ou faça uma pergunta específica para se aprofundar.

## Corrigir um bug

```bash
anote fix --error "TypeError: cannot read property 'id' of undefined"
anote fix src/handler.ts "o manipulador de webhook descarta eventos sob carga"
anote fix --loop --cmd "npm test"          # continue iterando até que os testes passem
```

## Escrever e commitar

```bash
anote generate "um middleware de limitador de taxa para Express" -o src/middleware/rateLimit.ts
anote test src/middleware/rateLimit.ts --write
anote commit                                # mensagem de commit gerada pela IA
```

## Revisar antes de enviar

```bash
anote diff --staged                         # revisar alterações em estágio
anote review --pr 42                        # ou revisar um PR aberto no GitHub
anote security --severity high              # auditoria OWASP Top 10
```

## Abrir um pull request

```bash
anote pr --gh                               # gerar descrição, abrir com o CLI gh
```

## Refatorar com segurança

```bash
anote refactor src/legacy.ts "extrair a lógica de validação para sua própria função" --dry-run
anote refactor src/legacy.ts "extrair a lógica de validação para sua própria função" --auto
```

Sempre tente `--dry-run` primeiro em qualquer coisa que você ainda não revisou.

## Continue trabalhando enquanto faz outra coisa

```bash
anote watch "src/**/*.ts"                   # reanalisar a cada salvamento
```

## Documentar enquanto avança

```bash
anote docs src/api.ts --style jsdoc
anote changelog --since v1.2.0
```

## Próximos passos

- [Biblioteca de prompts](prompt-library.md) — pontos de partida para copiar e colar
- [Comandos do CLI](../cli/commands.md) — referência completa de flags
