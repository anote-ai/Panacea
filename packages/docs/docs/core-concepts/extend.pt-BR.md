# Estender Panacea

Duas maneiras de personalizar como o Panacea se comporta em seu projeto: **CLAW.md** para instruções persistentes e **hooks** para executar seus próprios comandos em torno das chamadas de ferramentas.

## CLAW.md — memória do projeto

`CLAW.md` é um arquivo markdown que o Panacea lê para o contexto do projeto — a mesma ideia de um README voltado para o agente em vez de um humano. `anote init` gera um automaticamente, pré-preenchido com sua pilha detectada e comandos de verificação (teste/lint/construção):

```markdown
# CLAW.md

Este arquivo fornece orientações para o Anote AI ao trabalhar com código neste repositório.

## Visão geral do projeto

<!-- Descreva o que este projeto faz -->

## Pilha

TypeScript · Next.js

## Verificação

Execute estes antes de considerar uma alteração como completa:

  npm test
  npm run lint

## Acordo de trabalho

- Leia arquivos relevantes antes de fazer alterações
- Execute os comandos de verificação após modificar a lógica
- Mantenha as alterações pequenas e focadas
- Prefira editar arquivos existentes em vez de criar novos
```

Edite-o livremente — adicione notas de arquitetura, convenções ou coisas que o agente continua errando. O Panacea o lê no início de cada sessão naquele diretório.

## Hooks — execute seus próprios comandos em torno das chamadas de ferramentas

Hooks executam um comando shell antes (`preToolUse`) ou depois (`postToolUse`) de cada chamada de ferramenta, configurados em `.anote.json`:

```json
{
  "hooks": {
    "preToolUse": ["./scripts/check-tool-policy.sh"],
    "postToolUse": ["npx prettier --write ."]
  }
}
```

**Semântica do código de saída:**

| Código de saída | Efeito |
|---|---|
| `0` | Permitir — stdout é capturado como uma mensagem informativa |
| `2` | Negar — stdout é capturado como o motivo, mostrado ao agente |
| qualquer outro | Avisar, mas permitir |

Use `preToolUse` para bloquear comandos arriscados ou impor políticas antes que eles sejam executados; use `postToolUse` para coisas como autoformatação após cada edição.

## Próximos passos

- [Explore o diretório .anote](anote-directory.md) — onde CLAW.md e a configuração estão
- [Modos de permissão](../use-panacea/permission-modes.md) — a outra alavanca sobre o que o agente pode fazer
