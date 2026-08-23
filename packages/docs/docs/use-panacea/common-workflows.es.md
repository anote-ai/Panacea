# Flujos de trabajo comunes

Patrones paso a paso para tareas cotidianas con el CLI de Panacea.

## Explorar una base de código desconocida

```bash
anote explain                       # genera un recorrido CODEBASE.md
anote explain src/auth.ts "¿cómo funciona esto?"
anote index && anote search "validación JWT"
```

`explain` sin argumentos escribe una visión general de `CODEBASE.md` de todo el repositorio. Apúntalo a un archivo o haz una pregunta específica para profundizar.

## Arreglar un error

```bash
anote fix --error "TypeError: cannot read property 'id' of undefined"
anote fix src/handler.ts "el manejador de webhook descarta eventos bajo carga"
anote fix --loop --cmd "npm test"          # sigue iterando hasta que las pruebas pasen
```

## Escribir y confirmar

```bash
anote generate "un middleware limitador de tasa para Express" -o src/middleware/rateLimit.ts
anote test src/middleware/rateLimit.ts --write
anote commit                                # mensaje de confirmación generado por IA
```

## Revisar antes de enviar

```bash
anote diff --staged                         # revisar cambios en preparación
anote review --pr 42                        # o revisar un PR abierto en GitHub
anote security --severity high              # auditoría OWASP Top 10
```

## Abrir una solicitud de extracción

```bash
anote pr --gh                               # generar descripción, abrir con gh CLI
```

## Refactorizar de manera segura

```bash
anote refactor src/legacy.ts "extraer la lógica de validación en su propia función" --dry-run
anote refactor src/legacy.ts "extraer la lógica de validación en su propia función" --auto
```

Siempre intenta `--dry-run` primero en cualquier cosa que no hayas revisado aún.

## Sigue trabajando mientras haces otra cosa

```bash
anote watch "src/**/*.ts"                   # reanalizar en cada guardado
```

## Documentar mientras avanzas

```bash
anote docs src/api.ts --style jsdoc
anote changelog --since v1.2.0
```

## Próximos pasos

- [Biblioteca de prompts](prompt-library.md) — puntos de partida para copiar y pegar
- [Comandos de CLI](../cli/commands.md) — referencia completa de flags
