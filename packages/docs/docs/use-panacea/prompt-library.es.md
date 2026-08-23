# Biblioteca de Prompts

Copia y pega prompts para `anote ask`, `anote chat` y `anote fix`, organizados por tarea.

## Comprendiendo el código

```bash
anote ask "¿qué hace esta base de código, a un alto nivel?"
anote ask --file src/payments/webhook.ts "guíame a través de este archivo línea por línea"
anote ask "¿dónde se configura el limitador de tasa y cuáles son los límites?"
anote ask "¿qué se rompería si eliminara la capa de caché aquí?"
```

## Depuración

```bash
anote fix --error "$(cat error.log)"
anote ask "¿por qué falla esta prueba intermitentemente pero no de manera consistente?"
anote fix src/db/pool.ts "las conexiones no se están liberando de nuevo al grupo"
```

## Revisión de código

```bash
anote review --file src/auth/session.ts
anote review --pr 42
anote diff --staged -c "enfocarse en el manejo de errores y casos extremos"
```

## Refactorización

```bash
anote refactor src/utils.ts "divide esto en funciones más pequeñas y de un solo propósito" --dry-run
anote ask "¿hay una manera más simple de expresar esta lógica?" --file src/parser.ts
anote migrate --from "moment" --to "date-fns"
```

## Escribiendo pruebas

```bash
anote test src/utils/validate.ts --coverage --write
anote ask "¿qué casos extremos me faltan para esta función?" --file src/utils/validate.ts
```

## Seguridad y rendimiento

```bash
anote security --severity high
anote perf --focus "base de datos,tamaño del paquete"
```

## Documentación

```bash
anote docs src/api/client.ts --style jsdoc
anote changelog --since v1.2.0
anote explain --stdout                       # resumen rápido de la arquitectura
```

## Próximos pasos

- [Flujos de trabajo comunes](common-workflows.md)
- [Comandos de CLI](../cli/commands.md)
