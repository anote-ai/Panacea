# Extender Panacea

Dos formas de personalizar cómo se comporta Panacea en tu proyecto: **CLAW.md** para instrucciones persistentes, y los **hooks** para ejecutar tus propios comandos alrededor de las llamadas a herramientas.

## CLAW.md — memoria del proyecto

`CLAW.md` es un archivo markdown que Panacea lee para obtener contexto del proyecto — la misma idea que un README, pero dirigido al agente en lugar de a un humano. `anote init` genera uno automáticamente, prellenado con tu stack detectado y comandos de verificación (test/lint/build):

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

Edítalo libremente — añade notas de arquitectura, convenciones, o cosas en las que el agente sigue equivocándose. Panacea lo lee al comienzo de cada sesión en ese directorio.

## Hooks — ejecuta tus propios comandos alrededor de las llamadas a herramientas

Los hooks ejecutan un comando de shell antes (`preToolUse`) o después (`postToolUse`) de cada llamada a herramienta, configurados en `.anote.json`:

```json
{
  "hooks": {
    "preToolUse": ["./scripts/check-tool-policy.sh"],
    "postToolUse": ["npx prettier --write ."]
  }
}
```

**Semántica de los códigos de salida:**

| Código de salida | Efecto |
|---|---|
| `0` | Permitir — stdout se captura como mensaje informativo |
| `2` | Denegar — stdout se captura como motivo, mostrado al agente |
| cualquier otro | Advertir pero permitir |

Usa `preToolUse` para bloquear comandos riesgosos o aplicar políticas antes de que se ejecuten; usa `postToolUse` para cosas como formateo automático después de cada edición.

## Próximos pasos

- [Explorar el directorio .anote](anote-directory.md) — dónde viven CLAW.md y la configuración
- [Modos de permiso](../use-panacea/permission-modes.md) — la otra palanca sobre lo que puede hacer el agente
