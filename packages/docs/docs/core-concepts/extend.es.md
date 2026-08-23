# Extender Panacea

Dos maneras de personalizar cómo se comporta Panacea en tu proyecto: **CLAW.md** para instrucciones persistentes y **hooks** para ejecutar tus propios comandos alrededor de las llamadas a herramientas.

## CLAW.md — memoria del proyecto

`CLAW.md` es un archivo markdown que Panacea lee para el contexto del proyecto — la misma idea que un README dirigido al agente en lugar de a un humano. `anote init` genera uno automáticamente, prellenado con tu stack detectado y comandos de verificación (test/lint/build):

```markdown
# CLAW.md

Este archivo proporciona orientación a Anote AI al trabajar con el código en este repositorio.

## Descripción del proyecto

<!-- Describe lo que hace este proyecto -->

## Stack

TypeScript · Next.js

## Verificación

Ejecuta estos comandos antes de considerar un cambio como completo:

  npm test
  npm run lint

## Acuerdo de trabajo

- Lee los archivos relevantes antes de hacer cambios
- Ejecuta los comandos de verificación después de modificar la lógica
- Mantén los cambios pequeños y enfocados
- Prefiere editar archivos existentes en lugar de crear nuevos
```

Edítalo libremente: añade notas de arquitectura, convenciones o cosas que el agente sigue cometiendo errores. Panacea lo lee al inicio de cada sesión en ese directorio.

## Hooks — ejecuta tus propios comandos alrededor de las llamadas a herramientas

Los hooks ejecutan un comando de shell antes (`preToolUse`) o después (`postToolUse`) de cada llamada a la herramienta, configurados en `.anote.json`:

```json
{
  "hooks": {
    "preToolUse": ["./scripts/check-tool-policy.sh"],
    "postToolUse": ["npx prettier --write ."]
  }
}
```

**Semántica del código de salida:**

| Código de salida | Efecto |
|---|---|
| `0` | Permitir — stdout se captura como un mensaje informativo |
| `2` | Denegar — stdout se captura como la razón, mostrada al agente |
| cualquier otro | Advertir pero permitir |

Usa `preToolUse` para bloquear comandos arriesgados o hacer cumplir políticas antes de que se ejecuten; usa `postToolUse` para cosas como autoformateo después de cada edición.

## Próximos pasos

- [Explorar el directorio .anote](anote-directory.md) — donde viven CLAW.md y la configuración
- [Modos de permiso](../use-panacea/permission-modes.md) — la otra palanca sobre lo que el agente puede hacer
