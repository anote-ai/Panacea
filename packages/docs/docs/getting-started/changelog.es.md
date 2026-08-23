# Registro de cambios

Panacea aún no publica un archivo de registro de cambios mantenido a mano; la fuente de verdad sobre lo que se ha enviado es:

- **[Lanzamientos de GitHub](https://github.com/anote-ai/Panacea/releases)** — lanzamientos etiquetados para el CLI, la extensión de VS Code y otros paquetes
- **[Historial de commits](https://github.com/anote-ai/Panacea/commits/main)** — cada cambio, en orden

## Genera uno para tu propio proyecto

El CLI puede escribir un registro de cambios a partir del historial de git para *tu* código:

```bash
anote changelog                    # desde la última etiqueta
anote changelog --since v1.2.0
anote changelog --dry-run          # imprimir en lugar de escribir CHANGELOG.md
```

Esto escribe en el `CHANGELOG.md` de tu proyecto, no en el de Panacea.
