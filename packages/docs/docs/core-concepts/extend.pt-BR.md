# Estender o Panacea

Duas formas de personalizar como o Panacea se comporta no seu projeto: **CLAW.md** para instruções persistentes, e **hooks** para executar seus próprios comandos ao redor das chamadas de ferramentas.

## CLAW.md — memória do projeto

`CLAW.md` é um arquivo markdown que o Panacea lê para obter contexto do projeto — a mesma ideia de um README, mas voltado para o agente em vez de um humano. O `anote init` gera um automaticamente, pré-preenchido com seu stack detectado e comandos de verificação (test/lint/build):

```markdown
# CLAW.md

This file provides guidance to Anote AI when working with code in this repository.

## Project overview

<!-- Describe what this project does -->

## Stack

TypeScript · Next.js

## Verification

Run these before considering a change complete:

  npm test
  npm run lint

## Working agreement

- Read relevant files before making changes
- Run the verification commands after modifying logic
- Keep changes small and focused
- Prefer editing existing files over creating new ones
```

Edite livremente — adicione notas de arquitetura, convenções, ou coisas que o agente continua errando. O Panacea o lê no início de cada sessão naquele diretório.

## Hooks — execute seus próprios comandos ao redor das chamadas de ferramentas

Hooks executam um comando shell antes (`preToolUse`) ou depois (`postToolUse`) de cada chamada de ferramenta, configurados em `.anote.json`:

```json
{
  "hooks": {
    "preToolUse": ["./scripts/check-tool-policy.sh"],
    "postToolUse": ["npx prettier --write ."]
  }
}
```

**Semântica dos códigos de saída:**

| Código de saída | Efeito |
|---|---|
| `0` | Permitir — stdout é capturado como mensagem informativa |
| `2` | Negar — stdout é capturado como motivo, mostrado ao agente |
| qualquer outro | Avisar, mas permitir |

Use `preToolUse` para bloquear comandos arriscados ou aplicar políticas antes que sejam executados; use `postToolUse` para coisas como formatação automática após cada edição.

## Próximos passos

- [Explorar o diretório .anote](anote-directory.md) — onde ficam o CLAW.md e a configuração
- [Modos de permissão](../use-panacea/permission-modes.md) — a outra alavanca sobre o que o agente pode fazer
